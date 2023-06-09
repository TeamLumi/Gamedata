import json
import os
import time

from data_checks import get_average_time
from load_files import load_data
from pokemonUtils import GenForms, get_pokemon_info, get_pokemon_name, get_diff_form_dictionary

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
debug_file_path = os.path.join(repo_file_path, "Python_tasks", "Debug")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")

first_excecution_time_list = []
second_execution_time_list = []

def get_form_format(monsNo, formNo):
    mon_zeros = 3 - len(str(monsNo))
    form_zeros = 3 - len(str(formNo))
    return f"ZKN_FORM_{mon_zeros*'0'}{monsNo}_{form_zeros*'0'}{formNo}"

def remove_duplicates(path_dictionary):
    new_path = []
    for path_element in path_dictionary:
        if path_element not in new_path:
            new_path.append(path_element)
    return new_path

def remove_duplicate_forms(evolve):
    for pokemon in evolve.keys():
        evolve[pokemon]["path"] = remove_duplicates(evolve[pokemon]["path"])

def add_forms(evolve, graph):
    forms = GenForms()
    for form in forms:
        form_num = forms[form]
        pokemon_id = int(form[-7:-4])
        evolve_array = graph[form_num]["ar"]
        for pokemon in evolve.keys():
            if int(pokemon) != pokemon_id:
                continue
            initial_evolution_path = evolve[pokemon]["path"]
            form_evo_path = evolve[form_num]["path"]
            first_form_evo = form_evo_path[0]

            for evolution in initial_evolution_path:
                if len(evolve_array) != 0:
                    continue
                if evolution in evolve[first_form_evo]["path"]:
                    evolve[evolution]["path"].append(form_num)
                if len(evolve[form_num]["path"]) < 2:
                    evolution_path = evolve[evolution]["path"] + form_evo_path
                    evolve[form_num]["path"] = remove_duplicates(evolution_path)
                    evolve[evolution]["path"] = remove_duplicates(evolution_path)

def process_next_mon(queue, adjacent_nodes):
    forms = GenForms()
    next_mon = adjacent_nodes[2]
    next_form = adjacent_nodes[3]
    form_format = get_form_format(next_mon, next_form)

    if form_format in forms.keys():
        next_mon = forms[form_format]
        return next_mon, next_form
    return next_mon, next_form

def process_current_mon(queue):
    forms = GenForms()

    current_mon = queue.pop(0)
    current_form = queue.pop(0)
    form_format = get_form_format(current_mon, current_form)

    if form_format in forms.keys():
        current_mon = forms[form_format]

    return current_mon

def update_evolve_paths(evolve, current_mon, current_mon_path):
    evolve[current_mon]["path"].append(current_mon)
    evolve[current_mon]["path"] = list(dict.fromkeys(evolve[current_mon]["path"]))

    for i in range(len(current_mon_path)):
        evolve[current_mon_path[i]]["path"].append(current_mon)
        evolve[current_mon_path[i]]["path"] = [x for j, x in enumerate(evolve[current_mon_path[i]]["path"]) if x not in evolve[current_mon_path[i]]["path"][:j]]

def second_pathfind(pokemon, evolve, new_queue):

    while new_queue:
        current_mon = process_current_mon(new_queue)
        evolve[current_mon]["path"].append(pokemon)
        current_mon_path = evolve[current_mon]["path"]
        update_evolve_paths(evolve, current_mon, current_mon_path)

def first_pathfind(pokemon, evolve, graph, queue, new_queue):

    while queue:
        current_mon = process_current_mon(queue)
        
        adjacent_nodes = graph[current_mon]["ar"]
        if len(adjacent_nodes) == 0:
            continue
        
        next_mon, next_form = process_next_mon(queue, adjacent_nodes)

        evolve[next_mon]["path"] = evolve[current_mon]["path"] + [next_mon]
        for i in range(2, len(adjacent_nodes), 5):
            new_queue.append(adjacent_nodes[i])
            new_queue.append(adjacent_nodes[i + 1])

            second_pathfind(pokemon, evolve, new_queue)

            if current_mon != 751:
                new_queue.append(adjacent_nodes[i])
                new_queue.append(adjacent_nodes[i + 1])

        if current_mon != 751:
            queue.append(next_mon)
            queue.append(next_form)

        if not queue:
            queue = new_queue
            new_queue = []

    for extra in evolve[pokemon]["path"]:
        for i in range(0, len(graph[extra]["ar"]), 5):
            evolve[pokemon]["method"].append(graph[extra]["ar"][i])
        evolve[pokemon]["ar"].append(graph[extra]["ar"])

def start_pathfinding(evolve, graph):

    for pokemon in evolve.keys():
        queue = []
        queue.append(pokemon)
        queue.append(0)
        new_queue = []

        if pokemon not in evolve[pokemon]["path"]:
            evolve[pokemon]["path"].append(pokemon)
        first_pathfind(pokemon, evolve, graph, queue, new_queue)

def evolution_pathfinding():
    with open(os.path.join(input_file_path, 'EvolveTable.json'), "r", encoding="utf-8") as f:
        graphing = json.load(f)
    graph = graphing["Evolve"]
    forms = GenForms()
    evolve = {}
    for node in graph:
        evolve[node["id"]] = {"path": [], "method": [], "ar": []}

    start_pathfinding(evolve, graph)
    add_forms(evolve, graph)
    remove_duplicate_forms(evolve)

    with open(os.path.join(debug_file_path, "evolution.json"), "w", encoding = "utf-8") as output:
        json.dump(evolve, output, ensure_ascii=False, indent=2)
    return evolve

def get_mon_dex_info(pokemon, evolve):
    poke_info = get_pokemon_info(pokemon)
    poke_name = get_pokemon_name(pokemon)
    dex_info = {
        "value": pokemon,
        "text": poke_name,
        "type": poke_info["type"].upper()
        }
    if "dualtype" in poke_info.keys() and poke_info["dualtype"] != 0:
        dex_info["dualtype"] = poke_info["dualtype"].upper()
    dex_info["evolve"] = evolve
    dex_info["generation"] = 8
    dex_info["abilities"] = [poke_info['ability1'], poke_info['ability2'], poke_info['abilityH']]
    dex_info["dexNum"] = pokemon
    dex_info["form"] = 0
    if pokemon > 1010:
        for poke_form in diff_forms.keys():
            if poke_name in diff_forms[poke_form]:
                form_number = diff_forms[poke_form][4]
                og_num = diff_forms[poke_form][3]
        dex_info["dexNum"] = og_num
        dex_info["form"] = int(form_number)
        return dex_info

    return dex_info

def getPokedexInfo():
    pokedex = []
    evolutions = evolution_pathfinding()

    for pokemon in evolutions.keys():
        if pokemon >= 1456:
            continue
        evolve_path = evolutions[pokemon]["path"]
        if pokemon < 906 or pokemon > 1010:
            dex_info = get_mon_dex_info(pokemon, evolve_path)
        pokedex.append(dex_info)

    with open(os.path.join(output_file_path, "pokedex_info.json"), "w", encoding="utf-8") as output:
        json.dump(pokedex, output, ensure_ascii=False, indent=2)
    return pokedex

if __name__ == "__main__":
    diff_forms = get_diff_form_dictionary()
    full_data = load_data()
    getPokedexInfo()

if __name__ != "__main__":
    diff_forms = get_diff_form_dictionary()
    full_data = load_data()