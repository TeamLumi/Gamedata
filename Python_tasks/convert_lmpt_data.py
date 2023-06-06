import re
import json
import os
import csv
import unicodedata
import copy
from collections import defaultdict
from pokemonUtils import get_ability_string, get_pokemon_name, get_form_name, get_item_string, get_pokemon_name_dictionary, get_pokemon_info, get_nature_name, GenForms, get_form_pokemon_personal_id, create_diff_forms_dictionary, isSpecialPokemon, get_pokemon_from_trainer_info
from data_checks import check_bad_encounter, check_mons_list
from load_files import load_data

# Get the repo file path for cleaner path generating
repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
resources_filepath = os.path.join(repo_file_path, "Python_tasks", "Resources")
debug_file_path = os.path.join(repo_file_path, "Python_tasks", "Debug")
honeywork_cpp_filepath = os.path.join(input_file_path, "honeywork.cpp")
honeyroutes_filepath = os.path.join(repo_file_path, "Python_tasks", "Resources", "honeyroutes.json")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")
gym_leader_file_path = os.path.join(resources_filepath, "NewGymLeaders.json")
bad_encounters = []
final_list = {}
full_data = load_data()

with open(gym_leader_file_path, mode='r', encoding="utf-8") as f:
    gym_leader_data = json.load(f)

def getTrainerData(gymLeaderList):
    trainer_data, abilityList, pokedex, itemList, diff_forms = (
        full_data["raw_trainer_data"],
        full_data["abilities"],
        full_data["pokedex"],
        full_data["items"],
        full_data["diff_forms"]
    )
    gender = {"0": "MALE", "1": "FEMALE", "2": "NEUTRAL"}

    dic = {}
    full_list = []
    for battle_type, battles in gymLeaderList.items():
        for gym_leaders in battles:
            for gym_leader, trainer_ids in gym_leaders.items():
                trainers_list = []
                for trainer_id in trainer_ids:
                    fights = {}
                    trainer = next((t for t in trainer_data["TrainerPoke"] if t["ID"] == trainer_id), None)
                    output_format = "Tracker"
                    if trainer:
                        pokemon_list = get_pokemon_from_trainer_info(trainer, output_format)
                        fights["content"] = pokemon_list
                        fights["game"] = f"{gym_leader} Team {str(trainer_ids.index(trainer_id) + 1)}"
                        fights["name"] = gym_leader.split("(")[0].strip()
                        fights["type"] = battle_type
                        fights["route"] = f'{gym_leader.split("(")[1].strip(")")} Gym Leader' if len(gym_leader.split("(")) > 1 else "Elite Four Trainers"
                        fights["zoneId"] = None
                    trainers_list.append(fights)
                full_list.append(trainers_list)
    dic['1'] = full_list
    return dic

def match_honey_tree_data(match, honey_routes):
    array_regex = r"\[(.*?)\]\s*=\s*\{(.*?)\}"
    values_str = match.group(1)
    honey_trees = {}

    for line in values_str.split("\n"):
        line = line.strip()
        if not line:
            continue

        submatch = re.search(array_regex, line)
        if not submatch:
            continue

        key = submatch.group(1)
        values = [v.strip() for v in submatch.group(2).split(",")]
        if "AMPHAROS" not in values:
            honey_trees[honey_routes[key]] = values
    return honey_trees

def HoneyTreeData():
    const_regex = r"const\s+int32_t\s+HONEY_TREES\[\s*NUM_ZONE_ID\s*\]\[\s*10\s*\]\s*=\s*\{\s*([\s\S]*?)\};"

    with open(honeywork_cpp_filepath, "r") as file, open(honeyroutes_filepath, "r") as honey:
        honey_data = file.read()
        honey_routes = json.load(honey)

    # Extract honey trees data
    match = re.search(const_regex, honey_data)
    if match:
        return match_honey_tree_data(match, honey_routes)

def get_honey_tree_mons(routes):
    honey_encounter_data = HoneyTreeData()

    for key in honey_encounter_data.keys():
        for mon in honey_encounter_data[key]:
            if mon.capitalize() in routes[key]:
                continue
            if mon == "FARFETCHD":
                routes[key].append("Farfetch'd")
            else:
                routes[key].append(mon.capitalize())

def get_diff_form_mons(monsno, zoneID, encounters):
    pokedex, routeNames = ( full_data["pokedex"], full_data["routes"] )
    formNo = monsno//(2**16)
    lumi_formula_mon = monsno - (formNo * (2**16))
    for tracker_route, route in routeNames.items():

        if str(zoneID) not in route:
            continue
        pkmn_key = pokedex[str(lumi_formula_mon)] + str(formNo)

        temp_form_no = formNo
        if isSpecialPokemon(get_pokemon_name(int(lumi_formula_mon))):
            temp_form_no = 0
 
        check = check_bad_encounter(encounters, tracker_route, pkmn_key, lumi_formula_mon, temp_form_no, zoneID)
        if check != -1:
            bad_encounters.append(check)


def get_standard_mons(monsno, zoneID, encounters):
    pokedex, routeNames = ( full_data["pokedex"], full_data["routes"] )
    if monsno == 0:
        return
    for tracker_route, route in routeNames.items():
        if str(zoneID) not in route:
            continue
        encounters[str(tracker_route)].append(pokedex[str(monsno)])

def update_routes_with_mons(monsno, zoneID, encounters):
    if monsno < 2000:
        get_standard_mons(monsno, zoneID, encounters)
    else:
        get_diff_form_mons(monsno, zoneID, encounters)

def get_standard_rates(monsNo, zoneID, encounters, method, method_index):
    route_rates = full_data['rates']
    name_routes = full_data['name_routes']
    pokedex = full_data['pokedex']
    rates = full_data['rates']
    new_method = method
    pokemon_name = pokedex[str(monsNo)]
    for tracker_route, route in name_routes.items():
        if str(zoneID) not in route:
            continue

        if "gba" in new_method:
            if method_index == 2:
                new_method = "Surfing Incense"
            else:
                new_method = "Incense"
        if new_method == "Surfing Incense":
            rate = route_rates["Incense"][method_index]
        else:
            rate = route_rates[new_method][method_index]
        if pokemon_name not in encounters.keys():
            encounters[pokemon_name] = [[name_routes[tracker_route], new_method, rate, method_index]]
        else:
            if [name_routes[tracker_route], new_method, method_index, method_index] not in encounters[pokemon_name]:
                encounters[pokemon_name].append([name_routes[tracker_route], new_method, rate, method_index])

def get_diff_form_rates(monsNo, zoneID, encounters, method, method_index):
    route_rates, name_routes, pokedex, diff_forms, rates = ( full_data['rates'], full_data['name_routes'], full_data['pokedex'], full_data['diff_forms'], full_data['rates'] )
    new_method = method
    formNo = monsNo//(2**16)
    lumi_formula_mon = monsNo - (formNo * (2**16))
    for tracker_route, route in name_routes.items():

        if str(zoneID) not in route:
            continue
        pkmn_key = pokedex[str(lumi_formula_mon)] + str(formNo)

        temp_form_no = formNo
        if isSpecialPokemon(get_pokemon_name(int(lumi_formula_mon))):
            temp_form_no = 0

        check = check_bad_encounter(encounters, tracker_route, pkmn_key, lumi_formula_mon, temp_form_no, zoneID)
        if check != -1:
            bad_encounters.append(check)
            continue

        diff_forms_key = diff_forms[pkmn_key][1]

        if "gba" in new_method:
            if method_index == 2:
                new_method = "Surfing Incense"
            else:
                new_method = "Incense"
        if new_method == "Surfing Incense":
            rate = route_rates["Incense"][method_index]
        else:
            rate = route_rates[new_method][method_index]

        if diff_forms_key not in encounters.keys():
            encounters[diff_forms_key] = [[name_routes[tracker_route], new_method, rate, method_index]]
        else:
            if [name_routes[tracker_route], new_method, rate, method_index] not in encounters[diff_forms_key]:
                encounters[diff_forms_key].append([name_routes[tracker_route], new_method, rate, method_index])

def update_mons_rates(monsNo, zoneID, encounters, method, method_index):
    if monsNo == 0:
        return
    if monsNo < 2000:
        get_standard_rates(monsNo, zoneID, encounters, method, method_index)
    else:
        get_diff_form_rates(monsNo, zoneID, encounters, method, method_index)
    pass

def get_encounter_rates(route_mons, method, zoneID, encounters):
    for mon in route_mons:
        method_index = route_mons.index(mon)
        monsNo = mon['monsNo']
        update_mons_rates(monsNo, zoneID, encounters, method, method_index)
    pass

def getEncounterData():
    encounter_data, pokedex = ( full_data["raw_encounters"], full_data['pokedex'] )

    encounter_list = defaultdict(list)
    rates_list = defaultdict((list))
    for area in encounter_data['table']:
        check_mon_route_list = []
        zoneID = area['zoneID']
        for key in area.keys():
            if type(area[key]) == int:
                continue
            if type(area[key][0]) != dict:
                continue
            get_encounter_rates(area[key], key, zoneID, rates_list)
            for mon in area[key]:
                key_index = area[key].index(mon)
                monsno = mon['monsNo']
                check_mon_route_list.append([monsno, key, key_index, zoneID])
                update_routes_with_mons(monsno, zoneID, encounter_list)
        check = check_mons_list(check_mon_route_list, zoneID, final_list)
        if check != -1:
            final_list[zoneID] = check

    ##This is for adding the Trophy Garden daily mons
    for mon in encounter_data['urayama']:
        encounter_list['lmpt-39'].append(pokedex[str(mon['monsNo'])])

    ##This is for adding all of the Honey Tree encounters to the list
    get_honey_tree_mons(encounter_list)

    for key in encounter_list:
        encounter_list[key] = sorted(list(set(encounter_list[key])))

    my_keys = list(encounter_list.keys())
    my_keys.sort(key = lambda x: int(x.split('-')[1]))
    sorted_encounters = {i: encounter_list[i] for i in my_keys}

    with open(os.path.join(debug_file_path, 'bad_encounters.json'), 'w') as output:
        output.write(json.dumps(bad_encounters, default=tuple, indent=2))
    with open(os.path.join(output_file_path, 'Encounter_output.json'), 'w') as output:
        output.write(json.dumps(sorted_encounters, indent=2))

def pathfinding():
    with open(os.path.join(input_file_path, 'EvolveTable.json'), "r", encoding="utf-8") as f:
        graphing = json.load(f)
    graph = graphing["Evolve"]
    forms = GenForms()
    evolve = {}
    for node in graph:
        evolve[node["id"]] = {"path": [], "method": [], "ar": []}

    for pokemon in evolve.keys():
        queue = []
        queue.append(pokemon)
        queue.append(0)
        new_queue = []

        if pokemon not in evolve[pokemon]["path"]:
            evolve[pokemon]["path"].append(pokemon)

        while queue:
            current_mon = queue.pop(0)
            current_form = queue.pop(0)
            mon_zeros = 3 - len(str(current_mon))
            form_zeros = 3 - len(str(current_form))
            if f"ZKN_FORM_{mon_zeros*'0'}{current_mon}_{form_zeros*'0'}{current_form}" in forms.keys():
                current_mon = forms[f"ZKN_FORM_{mon_zeros*'0'}{current_mon}_{form_zeros*'0'}{current_form}"]
            adjacent_nodes = graph[current_mon]["ar"]
            if len(adjacent_nodes) != 0:
                next_mon = adjacent_nodes[2]
                next_form = adjacent_nodes[3]
                mon_zeros = 3 - len(str(next_mon))
                form_zeros = 3 - len(str(next_form))
                if f"ZKN_FORM_{mon_zeros*'0'}{next_mon}_{form_zeros*'0'}{next_form}" in forms.keys():
                    next_mon = forms[f"ZKN_FORM_{mon_zeros*'0'}{next_mon}_{form_zeros*'0'}{next_form}"]

                evolve[next_mon]["path"] = evolve[current_mon]["path"] + [next_mon]
                for i in range(2, len(adjacent_nodes), 5):
                    new_queue.append(adjacent_nodes[i])
                    new_queue.append(adjacent_nodes[i + 1])
                    while new_queue:
                        curr_mon = new_queue.pop(0)
                        curr_form = new_queue.pop(0)

                        mon_zeros = 3 - len(str(curr_mon))
                        form_zeros = 3 - len(str(curr_form))
                        if f"ZKN_FORM_{mon_zeros*'0'}{curr_mon}_{form_zeros*'0'}{curr_form}" in forms.keys():
                            curr_mon = forms[f"ZKN_FORM_{mon_zeros*'0'}{curr_mon}_{form_zeros*'0'}{curr_form}"]

                        ### This section is for the current pokemon
                        evolve[curr_mon]["path"].append(pokemon)
                        evolve[curr_mon]["path"].append(curr_mon)
                        evolve[curr_mon]["path"] = list(dict.fromkeys(evolve[curr_mon]["path"]))

                        ### This section is for the first pokemon in the chain
                        evolve[evolve[curr_mon]["path"][0]]["path"].append(curr_mon)
                        evolve[evolve[curr_mon]["path"][0]]["path"] = [x for i, x in enumerate(evolve[evolve[curr_mon]["path"][0]]["path"]) if x not in evolve[evolve[curr_mon]["path"][0]]["path"][:i]]

                        ### This section is for the second pokemon in the chain
                        if len(evolve[curr_mon]["path"]) > 1:
                            evolve[evolve[curr_mon]["path"][1]]["path"].append(curr_mon)
                            evolve[evolve[curr_mon]["path"][1]]["path"] = [x for i, x in enumerate(evolve[evolve[curr_mon]["path"][1]]["path"]) if x not in evolve[evolve[curr_mon]["path"][1]]["path"][:i]]

                        if len(evolve[curr_mon]["path"]) > 2:
                            evolve[evolve[curr_mon]["path"][2]]["path"].append(curr_mon)
                            evolve[evolve[curr_mon]["path"][2]]["path"] = [x for i, x in enumerate(evolve[evolve[curr_mon]["path"][2]]["path"]) if x not in evolve[evolve[curr_mon]["path"][2]]["path"][:i]]

                    ### Dewpider (751) currently evolves into Dewpider and creates an infinite loop
                    ### These can be taken away once that is fixed
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

    for form in forms:
        for pokemon in evolve.keys():
            if int(pokemon) != int(form[-7:-4]):
                continue
            for evolution in evolve[pokemon]["path"]:
                if len(graph[forms[form]]["ar"]) == 0:
                    if evolution in evolve[evolve[forms[form]]["path"][0]]["path"]:
                        evolve[evolution]["path"].append(forms[form])
                    if len(evolve[forms[form]]["path"]) < 2:
                        evolution_path = evolve[evolution]["path"] + evolve[forms[form]]["path"]
                        new_path = []
                        for path_element in evolution_path:
                            if path_element not in new_path:
                                new_path.append(path_element)
                        evolve[forms[form]]["path"] = new_path
                        evolve[evolution]["path"] = new_path

    for pokemon in evolve.keys():
        new_path = []
        for path_element in evolve[pokemon]["path"]:
            if path_element not in new_path:
                new_path.append(path_element)
        evolve[pokemon]["path"] = new_path
    with open(os.path.join(debug_file_path, "evolution.json"), "w", encoding = "utf-8") as output:
        json.dump(evolve, output, ensure_ascii=False, indent=2)
    return evolve

def get_mon_dex_info(pokemon, evolve):
    diff_forms = full_data['diff_forms']
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
    evolutions = pathfinding()

    for pokemon in evolutions.keys():
        if pokemon >= 1456:
            continue
        evolve = evolutions[pokemon]["path"]
        if pokemon < 906 or pokemon > 1010:
            dex_info = get_mon_dex_info(pokemon, evolve)
        pokedex.append(dex_info)

    with open(os.path.join(output_file_path, "pokedex_info.json"), "w", encoding="utf-8") as output:
        json.dump(pokedex, output, ensure_ascii=False, indent=2)
    return pokedex

if __name__ == "__main__":
    getPokedexInfo()
    getEncounterData()