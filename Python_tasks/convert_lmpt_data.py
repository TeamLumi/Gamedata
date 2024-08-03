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
                          get_pokemon_id_from_name, get_pokemon_name,
                          isSpecialPokemon, get_form_pokemon_personal_id)

# Get the repo file path for cleaner path generating
repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, constants.INPUT_NAME)
debug_file_path = os.path.join(repo_file_path, "Python_tasks", constants.DEBUG_NAME)
output_file_path = os.path.join(repo_file_path, "Python_tasks", constants.OUTPUT_NAME)

honeywork_cpp_filepath = os.path.join(input_file_path, "honeywork.cpp")
areas_file_path = os.path.join(input_file_path, 'areas_updated.csv')

bad_encounters = [] # This is to check any bad encounters that are in diff_forms
final_list = {} # This is for the encounters check to make sure none are being skipped over
areas_list = 0 # This is used for storing the areas in a list

first_excecution_time_list = [] # These are for adding times for length of executions in loops for debugging
second_execution_time_list = []

with open(areas_file_path, encoding="utf-8") as f:
    areas_list = [line.strip().split(',') for line in f.readlines()]

def create_zone_name_map():
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

def create_area_name_map():
    '''
    Creates a dictionary from the areas_copy.csv
    Format is {zone_name: zone_id}
    '''
    zone_dict = {}
    for place in areas_list:
        zone_index = int(areas_list.index(place) - 1)
        area_name = areas_list[zone_index][-3]
        zone_id = areas_list[zone_index][0]
        zone_dict[area_name] = zone_id
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

def get_display_name_from_zone_name(zone_name):
    if zone_name is None:
        return None

    display_name = next((e['labelName'] for e in display_names['labelDataArray'] 
                    if e.get('wordDataArray', [{}])[0].get('str') == zone_name), None)

    return display_name if display_name else None

def get_area_name_from_zone_name(zone_name):
    if zone_name is None:
        return None

    area_name = next((e['labelName'] for e in area_names['labelDataArray'] 
                    if e.get('wordDataArray', [{}])[0].get('str') == zone_name), None)

    return area_name if area_name else None

def find_zone_id(zone_name):
    display_name = get_display_name_from_zone_name(zone_name)
    area_name = get_area_name_from_zone_name(zone_name)

    if display_name:
        map_info_index = next((index for index, e in enumerate(map_info['ZoneData']) if e.get('MSLabel') == display_name), -1)
    else:
        map_info_index = next((index for index, e in enumerate(map_info['ZoneData']) if e.get('PokePlaceName') == area_name), -1)

    zone_id = map_info['ZoneData'][map_info_index].get('ZoneID', -1) if map_info_index != -1 else -1
    
    return zone_id if zone_id != -1 else None

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

def sort_dicts_by_keys_and_list(dicts_list, sort_key1, sort_key1_order):
    """
    Sorts a list of dictionaries by a given key in ascending order using sort_key1_order.
    The sorting order of the first key is specified by DOCS_ZONE_ORDER in Constants.py.
    """
    return sorted(dicts_list, key=lambda x: sort_key1_order.index(x[sort_key1]))

def sort_static_locations_by_route_name():
    route_data = {}

    for pokemon_name, encounters in static_encounters.items():
        for encounter in encounters:
            zoneId = encounter['zoneId']
            if zoneId not in route_data:
                route_data[zoneId] = []
            encounter_with_pokemon = encounter.copy()
            encounter_with_pokemon['pokemonName'] = pokemon_name
            route_data[zoneId].append(encounter_with_pokemon)

    with open(os.path.join(debug_file_path, 'static_area_locations.json'), 'w') as output:
        output.write(json.dumps(route_data, indent=2))

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

def honey_tree_encounter_data(mons_no_or_zoneId = "mons_no"):
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
                if mons_no_or_zoneId == "mons_no":
                    if constants.AMPHAROS_PLACE_HOLDER not in values:
                        honey_trees[zoneName] = [values, honey_routes[key][1]]
                elif mons_no_or_zoneId == "zoneId":
                    if constants.AMPHAROS_PLACE_HOLDER not in values:
                        honey_trees[str(zoneID)] = [values, honey_routes[key][1]]

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
    pokemonId = get_form_pokemon_personal_id(reverse_lumi_formula_mon, formNo)
    for tracker_route, route in routeNames.items():

        if str(zoneID) not in route:
            continue

        temp_form_no = formNo
        if isSpecialPokemon(get_pokemon_name(reverse_lumi_formula_mon, constants.GAME_MODE == "3.0")):
            temp_form_no = 0

        check = check_bad_encounter(encounters, tracker_route, reverse_lumi_formula_mon, temp_form_no, zoneID, constants.TRACKER_METHOD)
        if check == -1:
            encounters[str(tracker_route)].append(get_pokemon_name(pokemonId))
        else:
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
    if monsno < 2**16:
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

def get_standard_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index, mons_no_or_zoneId = "mons_no"):
    '''
    Iterates through the tracker routes
    '''
    new_method = method
    monsName = get_pokemon_name(monsNo)

    if any(str(zoneID) in route for route in name_routes.values()):
        zoneName = get_zone_name(zoneID)
        newZoneID = zoneID
        if zoneID == 297:
            newZoneID = 380
        new_method = check_for_incense(new_method, method_index)
        rate = get_route_rate(new_method, method_index, route_rates)
        encounter_list_order = {
            "routeName": zoneName,
            "pokemonName": monsName,
            "encounterType": new_method,
            "encounterRate": rate,
            "minLevel": minlevel,
            "maxLevel": maxlevel,
            "encounterTypeIndex": method_index,
            "zoneId": newZoneID
        }

        if mons_no_or_zoneId == "mons_no":
            if monsNo not in encounters:
                encounters[monsNo] = [encounter_list_order]
            elif encounter_list_order not in encounters[monsNo]:
                encounters[monsNo].append(encounter_list_order)
            elif "Incense" not in new_method:
                print("Something missing here?", method_index, monsNo, encounter_list_order)
        elif mons_no_or_zoneId == "zoneId":
            if str(newZoneID) not in encounters:
                encounters[str(newZoneID)] = [encounter_list_order]
            elif encounter_list_order not in encounters[str(newZoneID)]:
                encounters[str(newZoneID)].append(encounter_list_order)
            elif "Incense" not in new_method:
                print("Something missing here?", method_index, monsNo, encounter_list_order)

def get_diff_form_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index, mons_no_or_zoneId = "mons_no"):
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
    pokemon_id = get_form_pokemon_personal_id(reverse_lumi_formula_mon, formNo)
    monsName = get_pokemon_name(monsNo)

    temp_form_no = formNo
    if isSpecialPokemon(get_pokemon_name(monsNo)):
        temp_form_no = 0

    if any(str(zoneID) in route for route in name_routes.values()):
        zoneName = get_zone_name(zoneID)
        newZoneID = zoneID
        if zoneID == 297:
            newZoneID = 380
        new_method = check_for_incense(new_method, method_index)
        rate = get_route_rate(new_method, method_index, route_rates)
        encounter_list_order = {
            "routeName": zoneName,
            "pokemonName": monsName,
            "encounterType": new_method,
            "encounterRate": rate,
            "minLevel": minlevel,
            "maxLevel": maxlevel,
            "encounterTypeIndex": method_index,
            "zoneId": newZoneID
        }

        tracker_route = get_tracker_route(zoneID)

        check = check_bad_encounter(encounters, tracker_route, reverse_lumi_formula_mon, temp_form_no, zoneID)
        if check == -1:
            bad_encounters.append(check)
            return

        if mons_no_or_zoneId == "mons_no":
            if pokemon_id not in encounters:
                encounters[pokemon_id] = [encounter_list_order]
            elif encounter_list_order not in encounters[pokemon_id]:
                encounters[pokemon_id].append(encounter_list_order)
            elif "Incense" not in new_method:
                print("Something missing here?", method_index, pokemon_id, encounter_list_order)
        elif mons_no_or_zoneId == "zoneId":
            if str(newZoneID) not in encounters:
                encounters[str(newZoneID)] = [encounter_list_order]
            elif encounter_list_order not in encounters[str(newZoneID)]:
                encounters[str(newZoneID)].append(encounter_list_order)
            elif "Incense" not in new_method:
                print("Something missing here?", method_index, pokemon_id, encounter_list_order)

def update_mons_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index, mons_no_or_zoneId = "mons_no"):
    '''
    Branching paths based on MonsNo.
    2000 was chosen here as a buffer for any additional base forms in the game.
    This isn't perfect but will suffice for awhile
    '''
    if monsNo == 0:
        return
    if monsNo < 2000:
        get_standard_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index, mons_no_or_zoneId)
    else:
        get_diff_form_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index, mons_no_or_zoneId)

def get_encounter_rates(route_mons, method, zoneID, encounters, mons_no_or_zoneId = "mons_no"):
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
        update_mons_rates(monsNo, maxlevel, minlevel, zoneID, encounters, method, method_index, mons_no_or_zoneId)

def organize_honey_tree_list(mons_data, mons_no_or_zoneId = "mons_no"):
    '''
    This organizes the list of what goes into the list for the honey tree locations
    The route is the location that the honey tree/pokemon is found
    Rate is the percentage based on the count_mons_in_honey_trees function
    minlevel and maxlevel are the same in game
    There isn't a different slot for Honey trees so index is None
    zoneID is None for now for simplicity
    '''
    route = mons_data[0]
    method = constants.HONEY_TREE
    rate = mons_data[1]
    minlevel = mons_data[2]
    maxlevel = mons_data[2]
    index = None
    if mons_no_or_zoneId == "mons_no":
        zoneID = find_zone_id(route)
        if zoneID == None:
            zoneID = int(zone_id_dict[route])
    elif mons_no_or_zoneId == "zoneId":
        zoneID = route
    return {
        "routeName": route,
        "pokemonName": "",
        "encounterType": method,
        "encounterRate": rate,
        "minLevel": minlevel,
        "maxLevel": maxlevel,
        "encounterTypeIndex": index,
        "zoneId": zoneID
    }

def get_honey_tree_encounter_rates(rates_list, mons_no_or_zoneId = "mons_no"):
    '''
    Requires the honey_tree_encounter_data function and the list of all encounter rates
    This iterates through each of the mons in the honey_encounter_data and adds their rates to the rates list
    There is a check that ensures that the monsName is correctly spelled for the pokedex.
    '''
    honey_encounter_data = honey_tree_encounter_data(mons_no_or_zoneId)

    for mon in honey_encounter_data.keys():
        for mons_data in honey_encounter_data[mon]:
            monsName = constants.RIGHT_FARFETCHD if mon == constants.WRONG_FARFETCHD.capitalize() else mon
            if constants.GAME_MODE == "3.0":
                if monsName == "Wormadam" or monsName == "Burmy":
                    monsName = f"Plant Cloak {monsName}"
                if monsName == "Cherrim":
                    monsName = "Overcast Form Cherrim"
            monsNo = get_pokemon_id_from_name(monsName)
            zoneName = mons_data[0]

            encounter_list_order = organize_honey_tree_list(mons_data, mons_no_or_zoneId)
            encounter_list_order['pokemonName'] = monsName
            if mons_no_or_zoneId == "mons_no":
                if monsNo not in rates_list:
                    rates_list[monsNo] = [encounter_list_order]
                elif encounter_list_order not in rates_list[monsNo]:
                    rates_list[monsNo].append(encounter_list_order)
                elif method != "Incense" or method != "Surfing Incense":
                    print("Something missing here?", method_index, monsNo, encounter_list_order)
            elif mons_no_or_zoneId == "zoneId":
                if zoneName not in rates_list:
                    rates_list[zoneName] = [encounter_list_order]
                elif encounter_list_order not in rates_list[zoneName]:
                    rates_list[zoneName].append(encounter_list_order)

def get_trophy_garden_encounter_rates(trophy_garden_encounters, rates_list, mons_no_or_zoneId = "mons_no"):
    '''
    This is for adding the trophy garden encounter rates for each route
    '''
    for mon in trophy_garden_encounters:
        zoneId = 380
        zoneName = get_zone_name(zoneId) # This is the zoneID for Trophy Garden / Pokemon Mansion
        method = constants.TROPHY_GARDEN
        rate = constants.TROPHY_GARDEN_RATE
        minlevel = constants.TROPHY_GARDEN_LEVEL
        maxlevel = constants.TROPHY_GARDEN_LEVEL
        index = None
        monsNo = mon['monsNo']
        monsName = get_pokemon_name(monsNo)
        encounter_list_order = {
            "routeName": zoneName,
            "pokemonName": monsName,
            "encounterType": method,
            "encounterRate": rate,
            "minLevel": minlevel,
            "maxLevel": maxlevel,
            "encounterTypeIndex": index,
            "zoneId": zoneId
        }

        if mons_no_or_zoneId == "mons_no":
            if monsNo not in rates_list:
                rates_list[monsNo] = [encounter_list_order]
            elif encounter_list_order not in rates_list[monsNo]:
                rates_list[monsNo].append(encounter_list_order)
            elif method != "Incense" or method != "Surfing Incense":
                print("Something missing here?", monsNo, encounter_list_order)
        elif mons_no_or_zoneId == "zoneId":
            if str(zoneId) not in rates_list:
                rates_list[str(zoneId)] = [encounter_list_order]
            elif encounter_list_order not in rates_list[str(zoneId)]:
                rates_list[str(zoneId)].append(encounter_list_order)
            elif method != "Incense" or method != "Surfing Incense":
                print("Something missing here?", monsNo, encounter_list_order)

def getEncounterData(mons_no_or_zoneId = "mons_no"):
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
            get_encounter_rates(area[method], method, zoneID, rates_list, mons_no_or_zoneId)
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

    get_trophy_garden_encounter_rates(encounter_data[constants.TROPHY_GARDEN_NAME], rates_list, mons_no_or_zoneId)

    ## Add Marsh Random Encounters percent chance is 10%

    ##This is for adding all of the Honey Tree encounters to the list
    get_honey_tree_mons(encounter_list)
    get_honey_tree_encounter_rates(rates_list, mons_no_or_zoneId)

    for key in encounter_list:
        encounter_list[key] = sorted(list(set(encounter_list[key])))

    my_keys = list(encounter_list.keys())
    my_keys.sort(key = lambda x: int(x.split('-')[1]))
    sorted_encounters = {i: encounter_list[i] for i in my_keys}
    sorted_rates = sort_dict_by_keys(rates_list)
    if mons_no_or_zoneId == "mons_no":
        with open(os.path.join(input_file_path, 'pokemon_locations.json'), 'w') as output:
            output.write(json.dumps(sorted_rates, indent=2))
    elif mons_no_or_zoneId == "zoneId":
        with open(os.path.join(input_file_path, 'encounter_locations.json'), 'w') as output:
            output.write(json.dumps(sorted_rates, indent=2))
    with open(os.path.join(debug_file_path, 'bad_encounters.json'), 'w') as output:
        output.write(json.dumps(bad_encounters, default=tuple, indent=2))
    with open(os.path.join(output_file_path, 'Encounter_output.json'), 'w') as output:
        output.write(json.dumps(sorted_encounters, indent=2))

def writeEncounterDocData():
    with open(os.path.join(debug_file_path, 'pokemon_locations.json')) as f:
        data = json.load(f)
    largest_number = ["", 0]
    with open(os.path.join(debug_file_path, 'pokemon_locations.txt'), 'w') as output:
        for monsNo in data.keys():
            monsName = get_pokemon_name(int(monsNo))
            enc_dict = defaultdict(list)
            output.write(f"{monsName}|")
            sorted_data = sort_dicts_by_keys_and_list(data[monsNo], "routeName", constants.DOCS_ZONE_ORDER)
            for location in sorted_data:
                enc_type = location['encounterType']
                enc_location = location['routeName']
                if enc_type == constants.REGULAR_ENC:
                    enc_type = "Grass"
                elif enc_type == constants.SWARM:
                    enc_type = "Swarm"
                elif enc_type == constants.RADAR:
                    enc_type = "Radar"
                elif enc_type == constants.SURF_ENC:
                    enc_type = "Surfing"
                elif enc_type == constants.OLD_ENC:
                    enc_type = "Old Rod"
                elif enc_type == constants.GOOD_ENC:
                    enc_type = "Good Rod"
                elif enc_type == constants.SUPER_ENC:
                    enc_type = "Super Rod"
                enc_level = location['maxLevel']
                enc_rate = location['encounterRate']
                if enc_rate == "morning":
                    enc_rate_num = 10
                    enc_type = "Morning"
                else:
                    enc_rate_num = int(enc_rate.split('%')[0])
                enc_dict[enc_location].append([enc_type, enc_level, enc_rate_num])
            number = 0
            for enc_loc in enc_dict.keys():
                number += 1
                nest_list = enc_dict[enc_loc]
                route_dict = defaultdict(int)
                level_dict = {}
                for enc_type in nest_list:
                    level_dict[enc_loc] = enc_type[1]
                    route_dict[f"{enc_loc}|{enc_type[0]}"] += enc_type[2]
                for key in route_dict.keys():
                    split_key = key.split("|")
                    location = split_key[0]
                    enc_type = split_key[1]
                    level = level_dict[location]
                    rate = route_dict[key]
                    output.write(f"{location}|")
                    output.write(f"{enc_type}|")
                    output.write(f"{level}|")
                    output.write(f"{rate}%|")
            if number > largest_number[1] and monsName not in constants.NEW_TOP_10:
                largest_number = [monsName, number]
            output.write("\n")
    print("This is the largest number of encounters:",largest_number)

if __name__ != "__main__":
    full_data = load_data()
    area_names = full_data['area_names']
    display_names = full_data['area_display_names']
    map_info = full_data['map_info']
    trainer_data = full_data["raw_trainer_data"]

if __name__ == "__main__":
    start_time = time.time()
    full_data = load_data()
    
    pokedex = get_lumi_data(full_data["raw_pokedex"], get_pokemon_name)
    zone_dict = create_zone_name_map()
    zone_id_dict = create_area_name_map()
    route_rates = full_data['rates']
    name_routes = full_data['routes']
    rates = full_data['rates']
    area_names = full_data['area_names']
    display_names = full_data['area_display_names']
    map_info = full_data['map_info']
    static_encounters = full_data['static_encounters']

    diff_forms, NAME_MAP = get_diff_form_dictionary()
    getPokedexInfo()

    mid_time = time.time()
    print("Middle Execution time:", mid_time - start_time, "seconds")
    getEncounterData("mons_no")
    getEncounterData("zoneId")
    writeEncounterDocData()

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
