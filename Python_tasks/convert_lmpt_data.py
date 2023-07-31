import copy
import csv
import json
import os
import re
import time
import unicodedata
from collections import defaultdict, OrderedDict

import constants
from data_checks import check_bad_encounter, check_mons_list, get_average_time, check_monsName
from load_files import get_lumi_data, load_data
from pokedex_generator import getPokedexInfo
from pokemonUtils import (get_diff_form_dictionary,
                          get_pokemon_from_trainer_info,
                          get_pokemon_id_from_name, get_pokemon_name,
                          isSpecialPokemon, get_form_pokemon_personal_id)

# Get the repo file path for cleaner path generating
repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
debug_file_path = os.path.join(repo_file_path, "Python_tasks", "Debug")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")

honeywork_cpp_filepath = os.path.join(input_file_path, "honeywork.cpp")
areas_file_path = os.path.join(input_file_path, 'areas_copy.csv')

bad_encounters = [] # This is to check any bad encounters that are in diff_forms
final_list = {} # This is for the encounters check to make sure none are being skipped over
areas_list = 0 # This is used for storing the areas in a list

first_excecution_time_list = [] # These are for adding times for length of executions in loops for debugging
second_execution_time_list = []

with open(areas_file_path, encoding="utf-8") as f:
    areas_list = [line.strip().split(',') for line in f.readlines()]

def create_zone_id_map():
    '''
    Creates a dictionary from the areas_copy.csv
    Format is {zone_name: zone_id}
    '''
    zone_dict = {}
    for place in areas_list:
        zone_index = int(areas_list.index(place) - 1)
        zone_name = areas_list[zone_index][-1]
        zone_id = areas_list[zone_index][0]
        zone_dict[zone_name] = zone_id
    return zone_dict
 
def get_zoneID(zone_name):
    '''
    Uses the zone_dict created by create_zone_id_map.
    Format for that is {zone_name: zone_id}
    Returns the value of the 
    '''
    if zone_name in zone_dict.keys():
        return int(zone_dict[zone_name])
    else:
        return None

def get_zone_name(zoneID):
    '''
    Uses areas_copy.csv to get zoneName based on zoneID
    '''
    if not zoneID:
        print("Get a new zoneID")
        return
    zones = areas_list[zoneID + 1] # Adds 1 because this is the index of the csv rows which starts at -1 bc of the title
    zoneName = zones[3] if zones[3] != '' else zones[4]
    return zoneName

def get_tracker_route(zoneID):
    '''
    This is just used for the check_bad_encounter function
    It gets the name of the tracker_route (lmpt-##) based on the zoneIDs
    You can find this data in the name_routes.json
    '''
    route = next((route for tracker_route in name_routes.keys() for route in name_routes[tracker_route] if str(zoneID) in route), None)
    if route is not None:
        zoneName = get_zone_name(int(route))
        return zoneName
    return None

def sort_dict_by_keys(d):
    # Sorts a dictionary by it's keys
    sorted_dict = {}
    for key in sorted(d.keys()):
        sorted_dict[key] = d[key]
    return sorted_dict

def sort_keys_by_list(dct, lst):
    """
    Sorts a dictionary based on the order specified in lst and returns the sorted dictionary.
    """
    sorted_dict = OrderedDict(sorted(dct.items(), key=lambda x: lst.index(x[0])))
    return sorted_dict

def getTrainerData(gymLeaderList):
    '''
    This is a placeholder for the first 13 trainers for the tracker.
    Those being the gym leaders and the E4.
    '''

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
    '''
    Takes the match found from HoneyTreeData and adds all of the pokemon to a dictionary
    '''
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
    '''
    Using regex to convert a cpp file into a dictionary for easier use with Python
    '''
    with open(honeywork_cpp_filepath, "r") as file:
        honey_data = file.read()

    honey_routes = full_data['honey_routes']
    # Extract honey trees data
    match = re.search(constants.HONEY_TREE_CONST_REGEX, honey_data)
    if match:
        return match_honey_tree_data(match, honey_routes)

def get_honey_tree_mons(routes):
    '''
    Building on the dictionary created from getEncouterData()
    This adds all of the the pokemon found in the honeywork.cpp file to that dictionary
    '''
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
    '''
    Function that builds off of the encounters rates/locations code
    This counts every pokemon per route and adds them to the encounter rates dict
    This is also used to get the percentage of each mon per route (1 instance is 10%)
    This uses the honey_tree_encounter_data as an input.
    '''
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
    '''
    Original code and also a placeholder of the get_honey_tree_mons function
    This was added back in to allow the encounter_rates function to work properly
    This works in a similar way to the get_honey_tree_mons function
    '''
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
    '''
    This decodes the Lumi Formula ((FormNo * 2^16) + MonsNo).
    After decoding it, it checks if there are any special mons like Female Indeedee
    There is another check for any bad encounters in the list
    These can be found in the BAD_ENCOUNTER_LIST in constants.py
    If there are no bad encounters, every mon is added by name to a route for the tracker
    '''
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
    '''
    This add every pokemon to their route that isn't encoded with the Lumi formula
    '''
    routeNames = full_data["routes"] 
    if monsno == 0:
        return
    for tracker_route, route in routeNames.items():
        if str(zoneID) not in route:
            continue
        encounters[str(tracker_route)].append(get_pokemon_name(monsno))

def update_routes_with_mons(monsno, zoneID, encounters):
    '''
    Branching paths based on MonsNo.
    2000 was chosen here as a buffer for any additional base forms in the game.
    This isn't perfect but will suffice for awhile
    '''
    if monsno < 2000:
        get_standard_mons(monsno, zoneID, encounters)
    else:
        get_diff_form_mons(monsno, zoneID, encounters)

def get_route_rate(method, method_index, route_rates):
    '''
    This pulls data from the Rates.json to get the percentages for each encounter method
    '''
    if method == constants.SURFING_INCENSE:
        return route_rates[constants.INCENSE][method_index]
    elif method == constants.SWARM:
        return route_rates[constants.SWARM][0]
    elif method == constants.RADAR:
        return route_rates[constants.RADAR][3]
    return route_rates[method][method_index]

def check_for_incense(method, method_index):
    '''
    This function checks if the 3rd slot for the incense is being used.
    Returns a constant for each path.
    '''
    if "gba" in method:
        if method_index == 2:
            return constants.SURFING_INCENSE
        return constants.INCENSE
    return method

def get_standard_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index):
    '''
    Iterates through the tracker routes
    '''
    new_method = method
    monsName = get_pokemon_name(monsNo)

    if any(str(zoneID) in route for route in name_routes.values()):
        zones = areas_list[zoneID + 1]
        zoneName = zones[3] if zones[3] != '' else zones[4]
        new_method = check_for_incense(new_method, method_index)
        rate = get_route_rate(new_method, method_index, route_rates)
        encounter_list_order = {
            "pokemonName": monsName, 
            "encounterType": new_method,
            "encounterRate": rate,
            "minLevel": minlevel,
            "maxLevel": maxlevel,
            "encounterTypeIndex": method_index,
            "zoneId": zoneID
        }

        if zoneName not in encounters:
            encounters[zoneName] = [encounter_list_order]
        elif encounter_list_order not in encounters[zoneName] and new_method not in ["Incense", "Surfing Incense"]:
            encounters[zoneName].append(encounter_list_order)
        elif "Incense" not in new_method:
            print("Something missing here?", method_index, monsNo, encounter_list_order)

def get_diff_form_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index):
    '''
    This decodes the Lumi Formula ((FormNo * 2^16) + MonsNo).
    After decoding it, it checks if there are any special mons like Female Indeedee
    There is another check for any bad encounters in the list
    These can be found in the BAD_ENCOUNTER_LIST in constants.py
    If there are no bad encounters, every mon's location is added to their key which is their name
    '''
    new_method = method
    formNo = monsNo//(2**16)
    reverse_lumi_formula_mon = monsNo - (formNo * (2**16))
    pkmn_key = pokedex[str(reverse_lumi_formula_mon)] + str(formNo)
    diff_forms_key = diff_forms[pkmn_key][1]
    monsName = get_pokemon_name(monsNo)
    pokemon_id = get_form_pokemon_personal_id(reverse_lumi_formula_mon, formNo)

    temp_form_no = formNo
    if isSpecialPokemon(get_pokemon_name(monsNo)):
        temp_form_no = 0

    if any(str(zoneID) in route for route in name_routes.values()):
        zones = areas_list[zoneID + 1]
        zoneName = zones[3] if zones[3] != '' else zones[4]
        new_method = check_for_incense(new_method, method_index)
        rate = get_route_rate(new_method, method_index, route_rates)
        encounter_list_order = {
            "pokemonName": monsName,
            "encounterType": new_method,
            "encounterRate": rate,
            "minLevel": minlevel,
            "maxLevel": maxlevel,
            "encounterTypeIndex": method_index,
            "zoneId": zoneID
        }

        tracker_route = get_tracker_route(zoneID)

        check = check_bad_encounter(encounters, tracker_route, pkmn_key, reverse_lumi_formula_mon, temp_form_no, zoneID)
        if check == -1:
            bad_encounters.append(check)
            return

        if zoneName not in encounters:
            encounters[zoneName] = [encounter_list_order]
        elif encounter_list_order not in encounters[zoneName]:
            encounters[zoneName].append(encounter_list_order)
        elif "Incense" not in new_method:
            print("Something missing here?", method_index, pokemon_id, encounter_list_order)

def update_mons_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index):
    '''
    Branching paths based on MonsNo.
    2000 was chosen here as a buffer for any additional base forms in the game.
    This isn't perfect but will suffice for awhile
    '''
    if monsNo == 0:
        return
    if monsNo < 2000:
        get_standard_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index)
    else:
        get_diff_form_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index)

def get_encounter_rates(route_mons, method, zoneID, encounters):
    '''
    This is to start getting the encounter rates for each mon.
    route_mons is from each of the areas of the FieldEncountTable_d.json
    encounters is the dictionary full of lists for each mon and their corresponding areas
    There is a check for the method to ensure the following:
    It is the 1st slot of Swarm
    It is the 4th slot of the Radar
    It then passes all of that info to update_mons_rates
    '''
    for method_index, mon in enumerate(route_mons):
        monsNo = mon['monsNo']
        maxlevel, minlevel = mon['maxlv'], mon['minlv']
        if method == constants.SWARM and method_index != 0:
            continue
        if method == constants.RADAR and method_index != 3:
            continue
        update_mons_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index)

def organize_honey_tree_list(mons_data):
    '''
    This organizes the list of what goes into the list for the honey tree locations
    The route is the location that the honey tree/pokemon is found
    Rate is the percentage based on the count_mons_in_honey_trees function
    minlevel and maxlevel are the same in game
    There isn't a different slot for Honey trees so index is None
    zoneID is None for now for simplicity
    '''
    zoneName = mons_data[0]
    method = constants.HONEY_TREE
    rate = mons_data[1]
    minlevel = mons_data[2]
    maxlevel = mons_data[2]
    index = None
    zoneID = None
    return {
        "pokemonName": "", 
        "encounterType": method,
        "encounterRate": rate,
        "minLevel": minlevel,
        "maxLevel": maxlevel,
        "encounterTypeIndex": index,
        "zoneId": zoneID
    }

def get_honey_tree_encounter_rates(rates_list):
    '''
    Requires the honey_tree_encounter_data function and the list of all encounter rates
    This iterates through each of the mons in the honey_encounter_data and adds their rates to the rates list
    There is a check that ensures that the monsName is correctly spelled for the pokedex.
    '''
    honey_encounter_data = honey_tree_encounter_data()

    for mon in honey_encounter_data.keys():
        for mons_data in honey_encounter_data[mon]:
            monsName = constants.RIGHT_FARFETCHD if mon == constants.WRONG_FARFETCHD.capitalize() else mon
            check_monsName(monsName)
            monsNo = get_pokemon_id_from_name(monsName)
            zoneName = mons_data[0]

            encounter_list_order = organize_honey_tree_list(mons_data)
            encounter_list_order['pokemonName'] = monsName
            if zoneName not in rates_list:
                rates_list[zoneName] = [encounter_list_order]
            elif encounter_list_order not in rates_list[zoneName]:
                rates_list[zoneName].append(encounter_list_order)
            elif method != "Incense" or method != "Surfing Incense":
                print("Something missing here?", method_index, monsNo, encounter_list_order)

def get_trophy_garden_encounter_rates(trophy_garden_encounters, rates_list):
    '''
    This is for adding the trophy garden encounter rates for each route
    '''
    for mon in trophy_garden_encounters:
        zoneName = get_zone_name(297) # This is the zoneID for Trophy Garden
        method = constants.TROPHY_GARDEN
        rate = constants.TROPHY_GARDEN_RATE
        minlevel = constants.TROPHY_GARDEN_LEVEL
        maxlevel = constants.TROPHY_GARDEN_LEVEL
        index = None
        monsNo = mon['monsNo']
        monsName = get_pokemon_name(monsNo)
        encounter_list_order = {
            "pokemonName": monsName, 
            "encounterType": method,
            "encounterRate": rate,
            "minLevel": minlevel,
            "maxLevel": maxlevel,
            "encounterTypeIndex": index,
            "zoneId": 297
        }

        if zoneName not in rates_list:
            rates_list[zoneName] = [encounter_list_order]
        elif encounter_list_order not in rates_list[zoneName]:
            rates_list[zoneName].append(encounter_list_order)
        elif method != "Incense" or method != "Surfing Incense":
            print("Something missing here?", method_index, monsNo, encounter_list_order)

def getEncounterData():
    '''
    This is the main function to get all encounter data
    This includes each pokemon's location data and each route's list of pokemon
    '''
    encounter_data = full_data["raw_encounters"]
    encounter_list = defaultdict(list)
    rates_list = defaultdict((list))
    for area in encounter_data['table']:
        check_mon_route_list = []
        zoneID = area['zoneID']
        for method in area.keys():
            if type(area[method]) == int:
                continue
            if type(area[method][0]) != dict:
                continue
            get_encounter_rates(area[method], method, zoneID, rates_list)
            for method_index, mon in enumerate(area[method]):
                monsNo = mon['monsNo']
                check_mon_route_list.append([monsNo, method, method_index, zoneID])
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

def gatherEncounterDocData(route):
    enc_dict = {
        "Grass": [],
        "TOD": [],
        "Surf": [],
        "Fishing": [],
        "SR": [],
        "Honey Tree": [],
        "Incense": [],
        "MOD": []
        }
    for pokemon in route:
        if pokemon['encounterType'] == constants.REGULAR_ENC:
            enc_dict["Grass"].append(pokemon)
        elif pokemon['encounterType'] == constants.DAY_ENC or pokemon['encounterType'] == constants.NIGHT_ENC:
            enc_dict['TOD'].append(pokemon)
        elif pokemon['encounterType'] == constants.SURF_ENC:
            enc_dict['Surf'].append(pokemon)
        elif pokemon['encounterType'] in constants.ROD_ENC_LIST:
            enc_dict['Fishing'].append(pokemon)
        elif pokemon['encounterType'] == constants.SWARM or pokemon['encounterType'] == constants.RADAR:
            enc_dict['SR'].append(pokemon)
        elif pokemon['encounterType'] == constants.HONEY_TREE:
            enc_dict['Honey Tree'].append(pokemon)
        elif constants.INCENSE in pokemon['encounterType']:
            enc_dict['Incense'].append(pokemon)
        else:
            enc_dict['MOD'].append(pokemon)
            print(pokemon)
    return enc_dict

def writeEncounterDocData():
    with open(os.path.join(debug_file_path, 'encounter_locations.json')) as f:
        data = sort_keys_by_list(json.load(f), constants.DOCS_ZONE_ORDER)
    with open(os.path.join(debug_file_path, 'encounter_locations.txt'), 'w') as output:
        for route in data.keys():
            route_mons = gatherEncounterDocData(data[route])
            output.write(f"{route}|")
            if len(route_mons['Grass']) == 0:
                output.write(constants.GRASS_NONE)
            else:
                morningEnc = []
                for pokemon in route_mons['Grass']:
                    if pokemon['encounterRate'] != "morning":
                        output.write(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")
                    else:
                        morningEnc.append(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")
                for pokemon in morningEnc:
                    output.write(pokemon)


            if len(route_mons['TOD']) == 0:
                output.write(constants.TOD_NONE)
            else:
                for pokemon in route_mons['TOD']:
                    output.write(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")


            if len(route_mons['Incense']) == 0:
                for i in range(10):
                    output.write(f"{constants.DEFAULT_NONE}|")
            elif len(route_mons['Incense']) == 2 or len(route_mons['Incense']) == 3:
                for i in range(5):
                    output.write(f"{route_mons['Incense'][0]['pokemonName']}|{route_mons['Incense'][0]['maxLevel']}|{route_mons['Incense'][0]['encounterRate']}|")
                    output.write(f"{route_mons['Incense'][1]['pokemonName']}|{route_mons['Incense'][1]['maxLevel']}|{route_mons['Incense'][1]['encounterRate']}|")


            if len(route_mons['SR']) == 0:
                for i in range(2):
                    output.write(f"{constants.DEFAULT_NONE}|")
            elif len(route_mons['SR']) == 1 and route_mons['SR'][0]['encounterType'] == constants.SWARM:
                output.write(f"{route_mons['SR'][0]['pokemonName']}|{route_mons['SR'][0]['maxLevel']}|{route_mons['SR'][0]['encounterRate']}|")
                output.write(f"{constants.DEFAULT_NONE}|")
            elif len(route_mons['SR']) == 1 and route_mons['SR'][0]['encounterType'] == constants.RADAR:
                output.write(f"{constants.DEFAULT_NONE}|")
                output.write(f"{route_mons['SR'][0]['pokemonName']}|{route_mons['SR'][0]['maxLevel']}|{route_mons['SR'][0]['encounterRate']}|")
            else:
                for pokemon in route_mons['SR']:
                    output.write(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")


            if len(route_mons['MOD']) == 0:
                for i in range(16):
                    output.write(f"{constants.DEFAULT_NONE}|")
            else:
                for pokemon in route_mons['MOD']:
                    output.write(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")


            if len(route_mons['Fishing']) == 0:
                for i in range(constants.ROD_NONE):
                    output.write(f"{constants.DEFAULT_NONE}|")
            else:
                for pokemon in route_mons['Fishing']:
                    output.write(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")


            if len(route_mons['Surf']) == 0:
                for i in range(constants.SURF_NONE):
                    output.write(f"{constants.DEFAULT_NONE}|")
            else:
                for pokemon in route_mons['Surf']:
                    output.write(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")


            if len(route_mons['Incense']) == 0:
                for i in range(5):
                    output.write(f"{constants.DEFAULT_NONE}|")
            else:
                if len(route_mons['Incense']) == 1:
                    for i in range(5):
                        output.write(f"{route_mons['Incense'][0]['pokemonName']}|{route_mons['Incense'][0]['maxLevel']}|{route_mons['Incense'][0]['encounterRate']}|")
                elif len(route_mons['Incense']) == 3:
                        output.write(f"{route_mons['Incense'][2]['pokemonName']}|{route_mons['Incense'][2]['maxLevel']}|{route_mons['Incense'][2]['encounterRate']}|")


            if len(route_mons['Honey Tree']) == 0:
                for i in range(constants.HONEY_NONE):
                    output.write(f"{constants.DEFAULT_NONE}|")
            else:
                for pokemon in route_mons['Honey Tree']:
                    output.write(f"{pokemon['pokemonName']}|{pokemon['maxLevel']}|{pokemon['encounterRate']}|")
                if len(route_mons['Honey Tree']) < 8:
                    for i in range( 8 - len(route_mons['Honey Tree'])):
                        output.write(f"{constants.DEFAULT_NONE}|")
            output.write("\n")

if __name__ != "__main__":
    full_data = load_data()
    trainer_data = full_data["raw_trainer_data"]

if __name__ == "__main__":
    start_time = time.time()
    full_data = load_data()
    
    pokedex = get_lumi_data(full_data["raw_pokedex"], get_pokemon_name)
    zone_dict = create_zone_id_map()
    route_rates = full_data['rates']
    name_routes = full_data['routes']
    rates = full_data['rates']

    
    diff_forms, NAME_MAP = get_diff_form_dictionary()
    getPokedexInfo()

    mid_time = time.time()
    print("Middle Execution time:", mid_time - start_time, "seconds")
    getEncounterData()
    writeEncounterDocData()

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
