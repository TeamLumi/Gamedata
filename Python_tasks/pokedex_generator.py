import json
import os
import time
import csv

import constants
from data_checks import get_average_time, check_bad_dex_mon, is_valid_pokemon, check_egg_moveset
from load_files import load_data
from pokemonUtils import generate_form_name_to_pokemon_id, get_pokemon_info, get_pokemon_name, get_diff_form_dictionary, get_mons_no_and_form_no, get_form_pokemon_personal_id

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, constants.INPUT_NAME)
debug_file_path = os.path.join(repo_file_path, "Python_tasks", constants.DEBUG_NAME)
output_file_path = os.path.join(repo_file_path, "Python_tasks", constants.OUTPUT_NAME)
first_execution_list = []
second_execution_list = []

def get_form_format(monsNo, formNo):
    '''
    Returns the format of a mon based on the zkn_form file
    Requires the monsNo and formNo
    This should only be used with PID 1010 or greater
    '''
    mon_zeros = 3 - len(str(monsNo))
    form_zeros = 3 - len(str(formNo))
    return f"ZKN_FORM_{mon_zeros*'0'}{monsNo}_{form_zeros*'0'}{formNo}"

def remove_duplicates(path_dictionary):
    '''
    Removes any duplicate pokemon entry that exists.
    Uses the full path dictionary with all mons
    '''
    new_path = []
    for path_element in path_dictionary:
        if path_element not in new_path:
            new_path.append(path_element)
    return new_path

def remove_duplicate_forms(evolution_paths):
    '''
    Removes any duplicate forms after getting all of the evo data
    '''
    for pokemon in evolution_paths.keys():
        evolution_paths[pokemon]["path"] = remove_duplicates(evolution_paths[pokemon]["path"])

def add_forms(evolution_paths, graph):
    '''
    This is an optional function to add any different forms to the evolution paths
    It's mostly for the pokedex in the tracker as an easy way of handling different forms
    Included in this is mons like Rotom and Arceus that have different forms but they don't evolve into them
    '''
    invalid_pokemon = []
    for form in forms:
        pokemonID = forms[form]
        monsNo = int(form.split("_")[-2])
        evolve_array = graph[pokemonID]["ar"]
        is_invalid = check_bad_dex_mon(pokemonID, invalid_pokemon)
        if is_invalid != 1:
            continue
        for pokemon in evolution_paths.keys():
            if int(pokemon) != monsNo:
                continue
            initial_evolution_path = evolution_paths[pokemon]["path"]
            form_evo_path = evolution_paths[pokemonID]["path"]
            first_form_evo = form_evo_path[0]

            for evolution in initial_evolution_path:
                if len(evolve_array) != 0:
                    continue
                if evolution in evolution_paths[first_form_evo]["path"]:
                    evolution_paths[evolution]["path"].append(pokemonID)
                if len(evolution_paths[pokemonID]["path"]) < 2:
                    evolution_path = evolution_paths[evolution]["path"] + form_evo_path
                    evolution_paths[pokemonID]["path"] = remove_duplicates(evolution_path)
                    evolution_paths[evolution]["path"] = remove_duplicates(evolution_path)

def get_evolution_arrays(evolution_paths, graph):
    for pokemon in evolution_paths:
        for extra in evolution_paths[pokemon]["path"]:
            for i in range(0, len(graph[extra]["ar"]), 5):
                mon_evo_method = graph[extra]["ar"][i]
                evolution_paths[pokemon]["method"].append(mon_evo_method)
            evolution_paths[pokemon]["ar"].append(graph[extra]["ar"])

def process_next_mon(current_mon_evo_array):
    next_mon = current_mon_evo_array[2]
    next_form = current_mon_evo_array[3]
    form_format = get_form_format(next_mon, next_form)

    if form_format in forms.keys():
        next_mon = forms[form_format]
        return next_mon, next_form
    return next_mon, next_form

def process_current_mon(queue):
    current_mon = queue.pop(0)
    current_form = queue.pop(0)
    form_format = get_form_format(current_mon, current_form)

    if form_format in forms.keys():
        current_mon = forms[form_format]
        return current_mon, current_form

    return current_mon, current_form

def update_evolve_paths(evolution_paths, current_mon, current_mon_path):
    evolution_paths[current_mon]["path"].append(current_mon)
    evolution_paths[current_mon]["path"] = list(dict.fromkeys(evolution_paths[current_mon]["path"]))

    for index in range(len(current_mon_path)):
        evo_mon = evolution_paths[current_mon_path[index]]

        evolution_paths[current_mon_path[index]]["path"].append(current_mon)
        evolution_paths[current_mon_path[index]]["path"] = [
            pokemon for evo_index, pokemon in enumerate(evo_mon["path"])
            if pokemon not in set(evo_mon["path"][evo_index + 1:])
        ]

def get_second_pathfind_targets(evolution_paths, previous_mon, current_mon, graph):
    '''
    This is for getting the target evolution paths for evolutions
    The way this works is by checking two things
    Either the first_mon_path if there is more than 3 pokemon (This will happen for mons)
    '''
    targets = evolution_paths[previous_mon]["targets"]
    if current_mon in targets:
        return

    previous_mon_array = graph[previous_mon]["ar"]
    monsNo = current_mon
    formNo = 0
    if monsNo > 1010:
        monsNo, formNo = get_mons_no_and_form_no(current_mon)
    form_check = f"{monsNo}, {formNo}"
    if form_check not in str(previous_mon_array):
        return

    current_mon_path = evolution_paths[current_mon]["path"]
    first_mon = current_mon_path[0]
    first_mon_path = evolution_paths[first_mon]["path"]
    first_mon_array = graph[first_mon]["ar"]

    if len(first_mon_path) > 3:
        # This is for when a pokemon has a branching path at it's second form and not it's first form
        evolution_paths[previous_mon]["targets"].append(current_mon)
    elif len(first_mon_array) > 5:
        # This is for mons that have multiple evolutions in their first evo array like Burmy or Snorunt.
        evolution_paths[previous_mon]["targets"].append(current_mon)

def check_evo_path(first_pokemon, evolution_paths, current_mon, graph):
    if first_pokemon in evolution_paths[current_mon]["path"]:
        return
    current_mon_path = evolution_paths[current_mon]["path"]
    current_mon_path_exists = len(current_mon_path) > 0
    first_evolves_into_current = current_mon in graph[first_pokemon]['ar']
    if not current_mon_path_exists:
        if len(graph[current_mon]['ar']) > 0:
            current_mons_no, current_form_no = (graph[current_mon]['ar'][2], graph[current_mon]['ar'][3])
            current_mon_evo = get_form_pokemon_personal_id(current_mons_no, current_form_no)
            evo_path = [first_pokemon, current_mon, current_mon_evo]
            evolution_paths[current_mon]["path"].extend(evo_path)
            evolution_paths[current_mon_evo]["path"].extend(evo_path)
            return
        evolution_paths[current_mon]["path"].extend([first_pokemon, current_mon])
        return

    evolution_paths[current_mon]["path"].insert(1, first_pokemon)

def add_initial_mons(evolution_paths, current_mon, next_mon):
    targets = evolution_paths[current_mon]["targets"]
    current_mon_path = evolution_paths[current_mon]["path"]
    next_mon_path = evolution_paths[next_mon]["path"]
    if next_mon not in targets:
        evolution_paths[current_mon]["targets"].append(next_mon)
    if next_mon not in current_mon_path:
        evolution_paths[current_mon]["path"].append(next_mon)
    if next_mon not in next_mon_path:
        evolution_paths[next_mon]["path"].append(next_mon)

def second_pathfind(first_pokemon, evolution_paths, new_queue, graph):
    while new_queue:
        current_mon, current_form = process_current_mon(new_queue)
        check_evo_path(first_pokemon, evolution_paths, current_mon, graph)
        current_mon_path = evolution_paths[current_mon]["path"]
        update_evolve_paths(evolution_paths, current_mon, current_mon_path)
        get_second_pathfind_targets(evolution_paths, first_pokemon, current_mon, graph)

def first_pathfind(first_pokemon, evolution_paths, graph, first_queue, next_queue):
    '''
    first_pokemon is the PID of the root pokemon that started the pathfind
    Here's what this function is doing:
    1. Gets the first mon's PID and form from the queue
    2. If the current_mon_evo_array has nothing in it, then it continues to the next first_pokemon
    3. Initializes the first mon's evo array
    4. Processes the very next mon in the evo array
    5. If that next mon isn't in the current mon's targets, it's added to it.
    6. Adds current_mon's path to the next_mon's path as well as the next_mon
    7. Iterates over every evo that may be in the current_mon's array and repeats the same process as above
    8. Adds the next mon and form to the first_queue.
    9. Finally, this adds all of the evo methods for each pokemon and the evo arrays
    '''

    while first_queue:
        current_mon, current_mon_form = process_current_mon(first_queue)

        current_mon_evo_array = graph[current_mon]["ar"]
        if len(current_mon_evo_array) == 0:
            continue
        next_mon, next_mon_form = process_next_mon(current_mon_evo_array)

        add_initial_mons(evolution_paths, current_mon, next_mon)

        for i in range(2, len(current_mon_evo_array), 5):
            # Increments by 5 starting on the third value which is the target evolution
            next_current_mon = current_mon_evo_array[i]
            next_current_mon_form = current_mon_evo_array[i + 1]

            next_queue.append(next_current_mon)
            next_queue.append(next_current_mon_form)

            second_pathfind(first_pokemon, evolution_paths, next_queue, graph)

            next_queue.append(next_current_mon)
            next_queue.append(next_current_mon_form)

        first_queue.append(next_mon)
        first_queue.append(next_mon_form)

def start_pathfinding(evolution_paths, graph):
    '''
    This starts the pathfinding to find the evolution paths inside of the graph
    The graph is the EvolveTable that details only the very next evolution in the chain.
    The first part of this just adds the first pokemon to it's own evolution path.
    It also initializes the queue which goes until there are no more mons in subsequent evo array.
    It then passes all of the data to the first_pathfind
    '''
    for pokemon in evolution_paths.keys():
        queue = []
        queue.append(pokemon)
        queue.append(0)
        new_queue = []
        evo_path = evolution_paths[pokemon]["path"]
        if pokemon not in evo_path:
            evolution_paths[pokemon]["path"].append(pokemon)
        first_pathfind(pokemon, evolution_paths, graph, queue, new_queue)

def evolution_pathfinding():
    '''
    This initializes everything needed for the pathfinding and starts the process
    All of the pathfinding is output to the evolution.json without any alternate forms
    '''
    with open(os.path.join(input_file_path, 'EvolveTable.json'), "r", encoding="utf-8") as f:
        graphing = json.load(f)
    graph = graphing["Evolve"]
    evolution_paths = {}
    for node in graph:
        if (is_valid_pokemon(node["id"])):
            evolution_paths[node["id"]] = {"path": [], "method": [], "targets": [], "ar": []}

    start_pathfinding(evolution_paths, graph)
    get_evolution_arrays(evolution_paths, graph)

    with open(os.path.join(input_file_path, "evolution.json"), "w", encoding = "utf-8") as output:
        json.dump(evolution_paths, output, ensure_ascii=False, indent=2)

    add_forms(evolution_paths, graph)
    remove_duplicate_forms(evolution_paths)
    return evolution_paths

def get_mon_dex_info(pokemonId, evolution_paths):
    '''
    This is for the pokedex that is used in the Tracker.
    It initializes every pokemon for the pokedex and formats them
    The format is:
    {
        "value": pokemonID,
        "text": pokemon Name,
        "type": First type,
        "dualtype": second type,
        "evolve": evolution path for the pokemon,
        "generation": Always 8 for this game,
        "abilities": [
            ability1,
            ability2,
            hiddenAbility
        ],
        "dexNum": monsNo,
        "form": formNo
    }
    '''
    poke_info = get_pokemon_info(pokemonId)
    poke_name = get_pokemon_name(pokemonId)
    mons_no, form_no = get_mons_no_and_form_no(pokemonId)

    dex_info = {
        "value": pokemonId,
        "text": poke_name,
        "type": poke_info["type"].upper()
        }
    if "dualtype" in poke_info.keys() and poke_info["dualtype"] != 0:
        dex_info["dualtype"] = poke_info["dualtype"].upper()
    dex_info["evolve"] = evolution_paths
    dex_info["generation"] = 8
    dex_info["abilities"] = [poke_info['ability1'], poke_info['ability2'], poke_info['abilityH']]
    dex_info["dexNum"] = mons_no
    dex_info["form"] = form_no

    return dex_info

def export_pokedex_for_csv(pokemon):
    '''
    This is for the pokedex that is used in the Tracker.
    It initializes every pokemon for the pokedex and formats them
    The format is:
    {"value": pokemonID,
     "text": pokemon Name,
     "type": First type,
     "dualtype": second type,
     "evolve": evolution path for the pokemon,
     "generation": Always 8 for this game,
     "abilities": [
        ability1,
        ability2,
        hiddenAbility
     ],
     "dexNum": monsNo,
     "form": formNo}
    '''
    poke_info = get_pokemon_info(pokemon)
    poke_name = get_pokemon_name(pokemon)

    dex_info = {
        "value": pokemon,
        "text": poke_name,
        "type": poke_info["type"]
        }
    if "dualtype" in poke_info.keys() and poke_info["dualtype"] != 0:
        dex_info["dualtype"] = poke_info["dualtype"]
    dex_info["abilities"] = [poke_info['ability1'], poke_info['ability2'], poke_info['abilityH']]
    dex_info["learnset"] = poke_info['learnset']
    dex_info["tmLearnset"] = poke_info['tmLearnset']
    dex_info["eggLearnset"] = poke_info['eggLearnset']
    dex_info["tutorLearnset"] = poke_info['tutorLearnset']
    dex_info["baseStats"] = poke_info["baseStats"]
    dex_info["dexNum"] = poke_info['monsno']
    dex_info["form"] = poke_info['formno']
    dex_info["eggGroups"] = [constants.EGG_GROUPS[poke_info['egg_group1']], constants.EGG_GROUPS[poke_info['egg_group2']]]

    return dex_info

def getPokedexInfo():
    '''
    This iterates over every mon from the evolution_pathfinding
    There are limits surrounding the valid pokemon in the game and they are not allowed.
    '''
    pokedex = []
    evolutions = evolution_pathfinding()
    egg_move_dict = {}

    for pokemon in evolutions.keys():
        if pokemon == 0:
            continue
        if pokemon > constants.NAT_DEX_LENGTH:
            continue
        pokemon_name = get_pokemon_name(pokemon)
        is_valid = is_valid_pokemon(pokemon)
        egg_move_info = []
        if is_valid:
            egg_move_info = check_egg_moveset(pokemon)
        evolution_path = evolutions[pokemon]["path"]
        dex_info = get_mon_dex_info(pokemon, evolution_path)
        pokedex.append(dex_info)
        egg_move_dict[pokemon_name] = egg_move_info

    with open(os.path.join(output_file_path, "pokedex_info.json"), "w", encoding="utf-8") as output:
        json.dump(pokedex, output, ensure_ascii=False, indent=2)
    with open(os.path.join(debug_file_path, "egg_move_paths.json"), "w", encoding="utf-8") as output:
        json.dump(egg_move_dict, output, ensure_ascii=False, indent=2)
    return pokedex

def export_csv():
    '''
    This iterates over every mon from the evolution_pathfinding
    There are limits surrounding the valid pokemon in the game and they are not allowed.
    '''
    pokedex = []
    evolutions = evolution_pathfinding()

    with open(os.path.join(debug_file_path, "pokedex.csv") , mode='w', newline='') as file:
        writer = csv.writer(file)
        firstRow = ["Name",
            "PokemonID",
            "MonsNo",
            "FormNo",
            "Type 1",
            "Type 2",
            "Egg Group 1",
            "Egg Group 2",
            ]
        statBlock = [
            "HP",
            "Attack",
            "Defense",
            "Special Attack",
            "Special Defense",
            "Speed"
        ]
        for i in range(3):
            firstRow.append(f"Ability{i + 1}")
        for stat in statBlock:
            firstRow.append(stat)
        firstRow.append("Learnset")
        for i in range(99):
            firstRow.append("")
        firstRow.append("TM Learnset")
        for i in range(109):
            firstRow.append("")
        firstRow.append("Egg Learnset")
        for i in range(99):
            firstRow.append("")
        firstRow.append("Tutor Learnset")
        for i in range(99):
            firstRow.append("")
        writer.writerow(firstRow)

        for pokemon in evolutions.keys():
            if pokemon > constants.NAT_DEX_LENGTH:
                continue
            evolution_path = evolutions[pokemon]["path"]
            dex_info = export_pokedex_for_csv(pokemon)
            pokedex.append(dex_info)
            types = [dex_info['type']]
            if "dualtype" in dex_info.keys():
                types.append(dex_info['dualtype'])
            else:
                types.append("")
            abilities = dex_info['abilities']
            baseStats = dex_info['baseStats'].values()
            egg_groups = dex_info['eggGroups']

            learnsetKeys = list(dex_info['learnset'].keys())
            learnsetValues = list(dex_info['learnset'].values())
            actualLearnset = []
            for i in range(len(learnsetKeys)):
                actualLearnset.append(learnsetValues[i])
                actualLearnset.append(learnsetKeys[i])

            tmlearnset = list(dex_info['tmLearnset'].keys())
            egglearnset = list(dex_info['eggLearnset'].keys())
            tutorlearnset = list(dex_info['tutorLearnset'].keys())

            row = [dex_info['text'],
                dex_info['value'],
                dex_info['dexNum'],
                dex_info['form'],
                ]
            for _type in types:
                row.append(_type)
            for group in egg_groups:
                row.append(group)
            for ability in abilities:
                row.append(ability)
            for stat in baseStats:
                row.append(stat)
            for move in actualLearnset:
                row.append(move)
            if len(actualLearnset) < 100:
                for i in range(100 - len(actualLearnset)):
                    row.append("")
            for move in tmlearnset:
                row.append(move)
            if len(tmlearnset) < 110:
                for i in range(110 - len(tmlearnset)):
                    row.append("")
            for move in egglearnset:
                row.append(move)
            if len(egglearnset) < 100:
                for i in range(100 - len(egglearnset)):
                    row.append("")
            for move in tutorlearnset:
                row.append(move)
            if len(tutorlearnset) < 100:
                for i in range(100 - len(tutorlearnset)):
                    row.append("")

            writer.writerow(row)

    with open(os.path.join(debug_file_path, "pokedex_info_for_csv.json"), "w", encoding="utf-8") as output:
        json.dump(pokedex, output, ensure_ascii=False, indent=2)
    return pokedex

if __name__ == "__main__":
    diff_forms, NAME_MAP = get_diff_form_dictionary()
    full_data = load_data()
    forms = generate_form_name_to_pokemon_id()
    getPokedexInfo()
    export_csv()

if __name__ != "__main__":
    diff_forms, NAME_MAP = get_diff_form_dictionary()
    full_data = load_data()
    forms = generate_form_name_to_pokemon_id()