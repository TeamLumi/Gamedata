import copy
import csv
import json
import os
import re
import time
import unicodedata
from collections import defaultdict

import constants
from data_checks import check_bad_encounter, check_mons_list, get_average_time
from load_files import get_lumi_data, load_data
from pokedex_generator import getPokedexInfo
from pokemonUtils import (get_diff_form_dictionary,
                          get_pokemon_from_trainer_info,
                          get_pokemon_mons_no_from_name, get_pokemon_name,
                          isSpecialPokemon)

# Get the repo file path for cleaner path generating
repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
debug_file_path = os.path.join(repo_file_path, "Python_tasks", "Debug")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")

honeywork_cpp_filepath = os.path.join(input_file_path, "honeywork.cpp")
areas_file_path = os.path.join(input_file_path, 'areas_copy.csv')

bad_encounters = []
final_list = {}
areas_list = 0
first_excecution_time_list = [] # These are for adding times for length of executions in loops for debugging
second_execution_time_list = []


with open(areas_file_path, encoding="utf-8") as f:
    areas_list = [line.strip().split(',') for line in f.readlines()]

def get_zoneID(areaName):
    for places in areas_list:
        if areaName in places:
            zoneID = int(areas_list.index(places) - 1)
            return zoneID

def get_zone_name(zoneID):
    if not zoneID:
        print("Get a new zoneID")
        return
    zones = areas_list[zoneID + 1]
    zoneName = zones[3] if zones[3] != '' else zones[4]
    return zoneName

def sort_dict_by_keys(d):
    sorted_dict = {}
    for key in sorted(d.keys()):
        sorted_dict[key] = d[key]
    return sorted_dict

def getTrainerData(gymLeaderList):
    trainer_data = full_data["raw_trainer_data"]

    dic = {}
    full_list = []
    for battle_type, battles in gymLeaderList.items():
        for gym_leaders in battles:
            for gym_leader, trainer_ids in gym_leaders.items():
                trainers_list = []
                for trainer_id in trainer_ids:
                    fights = {}
                    trainer = next((t for t in trainer_data["TrainerPoke"] if t["ID"] == trainer_id), None)
                    if trainer:
                        pokemon_list = get_pokemon_from_trainer_info(trainer, constants.TRACKER_METHOD)
                        fights["content"] = pokemon_list
                        fights["game"] = f"{gym_leader} Team {str(trainer_ids.index(trainer_id) + 1)}"
                        fights["name"] = gym_leader.split("(")[0].strip()
                        fights["type"] = battle_type
                        fights["route"] = f'{gym_leader.split("(")[1].strip(")")} Gym Leader' if len(gym_leader.split("(")) > 1 else constants.E4_METHOD
                        fights["zoneId"] = None
                    trainers_list.append(fights)
                full_list.append(trainers_list)
    dic['1'] = full_list
    return dic

def match_honey_tree_data(match, honey_routes):
    values_str = match.group(1)
    honey_trees = {}

    for line in values_str.split("\n"):
        line = line.strip()
        if not line:
            continue

        submatch = re.search(constants.HONEY_TREE_MATCH_REGEX, line)
        if not submatch:
            continue

        key = submatch.group(1)
        values = [v.strip() for v in submatch.group(2).split(",")]
        if constants.AMPHAROS_PLACE_HOLDER not in values:
            honey_trees[honey_routes[key][0]] = values
    return honey_trees

def HoneyTreeData():
    with open(honeywork_cpp_filepath, "r") as file:
        honey_data = file.read()

    honey_routes = full_data['honey_routes']
    # Extract honey trees data
    match = re.search(constants.HONEY_TREE_CONST_REGEX, honey_data)
    if match:
        return match_honey_tree_data(match, honey_routes)

def get_honey_tree_mons(routes):
    honey_encounter_data = HoneyTreeData()

    for key in honey_encounter_data.keys():
        for mon in honey_encounter_data[key]:
            if mon.capitalize() in routes[key]:
                continue
            if mon == constants.WRONG_FARFETCHD:
                routes[key].append(constants.RIGHT_FARFETCHD)
            else:
                routes[key].append(mon.capitalize())

def count_mons_in_honey_trees(dict):
    result_dict = {}

    for route, mons in dict.items():
        if isinstance(mons, list):
            mon_counts = {}
            total_items = len(mons[0])
            level = mons[1]
            for mon in mons[0]:
                mon = mon.capitalize()
                if mon in mon_counts:
                    mon_counts[mon] += 1
                else:
                    mon_counts[mon] = 1

            for mon, count in mon_counts.items():
                percentage = f"{int((count / total_items)* 100)}%"
                if mon in result_dict:
                    result_dict[mon].append([route, percentage, level])
                else:
                    result_dict[mon] = [[route, percentage, level]]
    return result_dict

def honey_tree_encounter_data():

    with open(honeywork_cpp_filepath, "r") as file:
        data = file.read()
    honey_routes = full_data['honey_routes']
    # Extract honey trees data
    match = re.search(constants.HONEY_TREE_CONST_REGEX, data)
    if match:
        values_str = match.group(1)
        honey_trees = {}
        for line in values_str.split("\n"):
            line = line.strip()
            if not line:
                continue
            submatch = re.search(constants.HONEY_TREE_MATCH_REGEX, line)
            if submatch:
                key = submatch.group(1)
                zoneID = get_zoneID(key)
                if zoneID:
                    zoneName = get_zone_name(zoneID)
                values = [v.strip() for v in submatch.group(2).split(",")]
                if constants.AMPHAROS_PLACE_HOLDER not in values:
                    honey_trees[zoneName] = [values, honey_routes[key][1]]

    honey_trees = count_mons_in_honey_trees(honey_trees)

    return honey_trees

def get_diff_form_mons(monsno, zoneID, encounters):
    routeNames = full_data["routes"]
    formNo = monsno//(2**16)
    reverse_lumi_formula_mon = monsno - (formNo * (2**16))
    for tracker_route, route in routeNames.items():

        if str(zoneID) not in route:
            continue
        diff_key = get_pokemon_name(reverse_lumi_formula_mon) + str(formNo)
        pkmn_key = pokedex[str(reverse_lumi_formula_mon)] + str(formNo)

        temp_form_no = formNo
        if isSpecialPokemon(get_pokemon_name(monsno)):
            temp_form_no = 0

        check = check_bad_encounter(encounters, tracker_route, pkmn_key, reverse_lumi_formula_mon, temp_form_no, zoneID, constants.TRACKER_METHOD)
        if check != -1:
            bad_encounters.append(check)

def get_standard_mons(monsno, zoneID, encounters):
    routeNames = full_data["routes"] 
    if monsno == 0:
        return
    for tracker_route, route in routeNames.items():
        if str(zoneID) not in route:
            continue
        encounters[str(tracker_route)].append(get_pokemon_name(monsno))

def update_routes_with_mons(monsno, zoneID, encounters):
    if monsno < 2000:
        get_standard_mons(monsno, zoneID, encounters)
    else:
        get_diff_form_mons(monsno, zoneID, encounters)

def get_route_rate(method, method_index, route_rates):
    if method == constants.SURFING_INCENSE:
        return route_rates[constants.INCENSE][method_index]
    elif method == constants.SWARM:
        return route_rates[constants.SWARM][0]
    elif method == constants.RADAR:
        return route_rates[constants.RADAR][3]
    return route_rates[method][method_index]

def check_for_incense(method, method_index):
    if "gba" in method:
        if method_index == 2:
            return constants.SURFING_INCENSE
        return constants.INCENSE
    return method

def get_standard_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index):
    route_rates = full_data['rates']
    name_routes = full_data['routes']
    rates = full_data['rates']
    new_method = method
    monsName = get_pokemon_name(monsNo)

    for tracker_route in name_routes.keys():
        for route in name_routes[tracker_route]:
            if str(zoneID) not in route:
                continue
            zones = areas_list[int(route) + 1]
            zoneName = zones[3] if zones[3] != '' else zones[4]

            new_method = check_for_incense(new_method, method_index)
            rate = get_route_rate(new_method, method_index, route_rates)
            encounter_list_order = [zoneName, new_method, rate, minlevel, maxlevel, method_index]

            if monsName not in encounters.keys():
                encounters[monsName] = [encounter_list_order]
            else:
                if encounter_list_order not in encounters[monsName]:
                    encounters[monsName].append(encounter_list_order)

def get_diff_form_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index):
    route_rates, name_routes, rates = ( full_data['rates'], full_data['routes'], full_data['rates'] )
    new_method = method
    formNo = monsNo//(2**16)
    reverse_lumi_formula_mon = monsNo - (formNo * (2**16))
    for tracker_route in name_routes.keys():
        for route in name_routes[tracker_route]:

            if str(zoneID) not in route:
                continue
            zones = areas_list[int(route) + 1]
            zoneName = zones[3] if zones[3] != '' else zones[4]
            pkmn_key = pokedex[str(reverse_lumi_formula_mon)] + str(formNo)
            diff_forms_key = diff_forms[pkmn_key][1]
            monsName = get_pokemon_name(monsNo)

            temp_form_no = formNo
            if isSpecialPokemon(get_pokemon_name(monsNo)):
                temp_form_no = 0

            check = check_bad_encounter(encounters, tracker_route, pkmn_key, reverse_lumi_formula_mon, temp_form_no, zoneID)
            if check == -1:
                bad_encounters.append(check)
                continue

            new_method = check_for_incense(new_method, method_index)
            rate = get_route_rate(new_method, method_index, route_rates)
            encounter_list_order = [zoneName, new_method, rate, minlevel, maxlevel, method_index]


            if monsName not in encounters.keys():
                encounters[monsName] = [encounter_list_order]
            else:
                if encounter_list_order not in encounters[monsName]:
                    encounters[monsName].append(encounter_list_order)

def update_mons_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index):
    if monsNo == 0:
        return
    if monsNo < 2000:
        get_standard_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index)
    else:
        get_diff_form_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index)

def get_encounter_rates(route_mons, method, zoneID, encounters):
    for mon in route_mons:
        method_index = route_mons.index(mon)
        monsNo = mon['monsNo']
        maxlevel, minlevel = mon['maxlv'], mon['minlv']
        if method == constants.SWARM and method_index == 1:
            continue
        update_mons_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index)

def get_honey_tree_encounter_rates(rates_list):
    honey_encounter_data = honey_tree_encounter_data()

    for mon in honey_encounter_data.keys():
        for data in honey_encounter_data[mon]:
            route = data[0]
            monsName = constants.RIGHT_FARFETCHD if mon == constants.WRONG_FARFETCHD.capitalize() else mon
            monsNo = get_pokemon_mons_no_from_name(monsName)
            method = constants.HONEY_TREE
            rate = data[1]
            minlevel = data[2]
            maxlevel = data[2]
            index = None
            if monsNo == -1:
                print(monsName)
            if monsName not in rates_list:
                rates_list[monsName] = [[route, method, rate, minlevel, maxlevel, index]]
            else:
                rates_list[monsName].append([route, method, rate, minlevel, maxlevel, index])

def get_trophy_garden_encounter_rates(trophy_garden_encounters, rates_list):
    for mon in trophy_garden_encounters:
        zones = areas_list[297 + 1]
        zoneName = zones[3] if zones[3] != '' else zones[4]
        method = constants.TROPHY_GARDEN
        rate = constants.TROPHY_GARDEN_RATE
        minlevel = constants.TROPHY_GARDEN_LEVEL
        maxlevel = constants.TROPHY_GARDEN_LEVEL
        index = None
        monsNo = mon['monsNo']
        monsName = get_pokemon_name(monsNo)

        if monsName not in rates_list.keys():
            rates_list[monsName] = [zoneName, method, rate, minlevel, maxlevel, index]
        else:
            rates_list[monsName].append([zoneName, method, rate, minlevel, maxlevel, index])

def getEncounterData():
    encounter_data = full_data["raw_encounters"]
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
                monsNo = mon['monsNo']
                check_mon_route_list.append([monsNo, key, key_index, zoneID])
                update_routes_with_mons(monsNo, zoneID, encounter_list)
        check = check_mons_list(check_mon_route_list, zoneID, final_list)
        if check != -1:
            final_list[zoneID] = check
    ##This is for adding the Trophy Garden daily mons
    for mon in encounter_data[constants.TROPHY_GARDEN_NAME]:
        monsNo = mon['monsNo']
        encounter_list[constants.TROPHY_GARDEN_TRACKER_VAR].append(get_pokemon_name(monsNo))
    get_trophy_garden_encounter_rates(encounter_data[constants.TROPHY_GARDEN_NAME], rates_list)

    ##This is for adding all of the Honey Tree encounters to the list
    get_honey_tree_mons(encounter_list)
    get_honey_tree_encounter_rates(rates_list)

    for key in encounter_list:
        encounter_list[key] = sorted(list(set(encounter_list[key])))

    my_keys = list(encounter_list.keys())
    my_keys.sort(key = lambda x: int(x.split('-')[1]))
    sorted_encounters = {i: encounter_list[i] for i in my_keys}
    sorted_rates = sort_dict_by_keys(rates_list)
    with open(os.path.join(debug_file_path, 'encounter_locations.json'), 'w') as output:
        output.write(json.dumps(sorted_rates, indent=2))
    with open(os.path.join(debug_file_path, 'bad_encounters.json'), 'w') as output:
        output.write(json.dumps(bad_encounters, default=tuple, indent=2))
    with open(os.path.join(output_file_path, 'Encounter_output.json'), 'w') as output:
        output.write(json.dumps(sorted_encounters, indent=2))

if __name__ == "__main__":
    start_time = time.time()
    full_data = load_data()
    gym_leader_data = full_data['gym_leaders']
    pokedex = get_lumi_data(full_data["raw_pokedex"], get_pokemon_name)
    
    diff_forms = get_diff_form_dictionary()
    getPokedexInfo()

    mid_time = time.time()
    print("Middle Execution time:", mid_time - start_time, "seconds")
    getEncounterData()

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
