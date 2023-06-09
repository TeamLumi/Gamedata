import copy
import time

import constants
from load_files import load_data, get_lumi_data
from pokemonUtils import (get_form_name, get_form_pokemon_personal_id,
                          get_pokemon_name, get_pokemon_name, get_diff_form_dictionary)

def get_average_time(execution_times):
    return sum(execution_times) / len(execution_times)

def bad_encounter_data(pkmn_name, routeName, route):
    bad_encounters = []
    print('BAD ENCOUNTER', pkmn_name, routeName, route)
    bad_encounters.append({pkmn_name, routeName, route})
    return bad_encounters

def check_bad_encounter(encounters, tracker_route, pkmn_key, lumi_formula_mon, temp_form_no, zoneID, method=''):
    name_routes = full_data['name_routes']

    bad_encounters = []
    pokemonPersonalId = get_form_pokemon_personal_id(lumi_formula_mon, temp_form_no)

    if pokemonPersonalId is not None and any(substring in get_pokemon_name(pokemonPersonalId) for substring in constants.BAD_ENCOUNTER_LIST):
        bad_encounters.append(bad_encounter_data(get_pokemon_name(pokemonPersonalId), name_routes[tracker_route], zoneID))
        return bad_encounters
    elif pkmn_key not in diff_forms.keys():
        bad_encounters.append(bad_encounter_data(get_pokemon_name(lumi_formula_mon), name_routes[tracker_route], zoneID))
        return bad_encounters
    elif method == constants.TRACKER_METHOD:
        encounters[str(tracker_route)].append(diff_forms[pkmn_key][1])
        return -1
    else:
        return -2

def check_mons_list(pokemon_list, zoneID, final_list):
    original_list = []
    missing_list = []
    incense_count = 0
    radar_list = {zoneID: []}

    for mon in pokemon_list:
        if mon[1] in constants.REGULAR_ENC_LIST:
            original_list.append(mon[0])
    active_list = copy.deepcopy(original_list)

    active_list[9] = active_list[1]
    active_list[10] = active_list[4]
    active_list[11] = active_list[5]
    for mon in pokemon_list:
        if mon[1] == constants.RADAR:
            radar_list[zoneID].append(get_pokemon_name(mon[0]))
            active_list[1] = mon[0]
        if mon[1] in constants.INCENSE_LIST and mon[2] != 2 and incense_count < 2:
            incense_count += 1
            if incense_count == 1:
                active_list[4] = mon[0]
            if incense_count == 2:
                active_list[5] = mon[0]
    for mon in original_list:
        if mon == 0:
            continue
        pokemon_name = get_pokemon_name(mon)
        if mon not in active_list:
            missing_list.append(pokemon_name)

    unique_radar_list = list(set(radar_list[zoneID]))
    if len(unique_radar_list) > 1:
        print(radar_list)
    unique_list = list(set(missing_list))
    if len(unique_list) > 0:
        return unique_list
    return -1

if __name__ != "__main__":
    full_data = load_data()
    diff_forms = get_diff_form_dictionary()