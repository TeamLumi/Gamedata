import copy
import time
from collections import defaultdict

import constants
from load_files import load_data, get_lumi_data
from pokemonUtils import (get_form_name, get_form_pokemon_personal_id,
                          get_pokemon_name, get_pokemon_name, get_diff_form_dictionary,
                          get_pokemon_id_from_name)
from moveUtils import get_move_string, get_mon_full_learnset, get_egg_moves
from eggGroups import getEggGroupViaPokemonId, getPokemonIdsInEggGroup, pokemonIdsByEggGroup

def check_monsName(monsName):
    '''
    This checks that a pokemons name is formatted correctly specifically for the Honey trees
    '''
    monsNo = get_pokemon_id_from_name(monsName)
    if monsNo == -1:
        raise SyntaxError("This monsName is not formatted correctly to get a correct monsNo:", monsName)

def get_average_time(execution_times):
    # Do I really need to explain this one?
    return sum(execution_times) / len(execution_times)

def bad_encounter_data(pkmn_name, routeName=None, route=None):
    '''
    This is useful for checking whether there are bad encounters within the diff_forms
    '''
    bad_encounters = []
    if routeName == None and route == None:
        print("This is an invalid pokemon in the dex:", pkmn_name)
        bad_encounters.append([pkmn_name, "Pokedex"])
        return bad_encounters
    print('BAD ENCOUNTER', pkmn_name, routeName, route)
    bad_encounters.append({pkmn_name, routeName, route})
    return bad_encounters

def check_bad_encounter(encounters, tracker_route, pkmn_key, lumi_formula_mon, temp_form_no, zoneID, method=''):
    '''
    This checks the methods that are on each route and verifies that no pokemon is missing
    '''
    name_routes = full_data['name_routes']

    bad_encounters = []
    pokemonPersonalId = get_form_pokemon_personal_id(lumi_formula_mon, temp_form_no)
    is_valid = personal_table[pokemonPersonalId]['valid_flag']

    if pokemonPersonalId is not None and is_valid == 0:
        bad_encounter = bad_encounter_data(get_pokemon_name(pokemonPersonalId), name_routes[tracker_route], zoneID)
        bad_encounters.append(bad_encounter)
        return bad_encounters
    elif pkmn_key not in diff_forms.keys():
        bad_encounter = bad_encounter_data(get_pokemon_name(pokemonPersonalId), name_routes[tracker_route], zoneID)
        bad_encounters.append(bad_encounter)
        return bad_encounters
    elif method == constants.TRACKER_METHOD:
        encounters[str(tracker_route)].append(diff_forms[pkmn_key][1])
        return -1
    else:
        return -2

def check_bad_dex_mon(pokemonID, invalid_pokemon):
    pokemonName = get_pokemon_name(pokemonID)
    is_valid = personal_table[pokemonID]['valid_flag']
    if pokemonID is not None and is_valid == 0:
        invalid_pokemon.append(bad_encounter_data(pokemonName))
        return invalid_pokemon
    return 1

def check_mons_list(pokemon_list, zoneID, final_list):
    '''
    This checks the methods that are on each route and verifies that no pokemon is missing.
    Here's what's happening because it's mighty confusing:
        Generated a list of the ground_mons
        Made a copy of that list to make changes to it.
        In the copy of the list, I did the following:
            moved the 2nd slot mon to the 10th slot (and deleted the pokemon that was in slot 10 before, same thing with the rest)
            moved the 5th slot mon to the 11th slot
            moved the 6th slot mon to the 12th slot
        For the radar and incense mons I did the following to the copy of the list:
            Changed the 2nd slot of the list to be the 4th slot of the radar
            Changed the 5th slot to be the 1st slot of the very first incense category ('gbaRuby' unless there's something out of order).
            Changed the 6th slot to be the 2nd slot of the incense.
        Compared the contents of the two lists (original_list and copy_of_list) to find if there were pokemon that were in the original_list and not in the copy_of_list
        If there were pokemon that were in original_list and not in the copy_of_list, a flag goes up and throws a warning.
    '''
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

def check_egg_moveset(pokemonID):
    egg_move_path = defaultdict(list)
    egg_groups_list = []

    learnset = get_mon_full_learnset(pokemonID)
    mon_egg_group = getEggGroupViaPokemonId(pokemonID)
    baby_pokemon_id = evolution_dex[str(pokemonID)]['path'][0]
    egg_set = get_egg_moves(baby_pokemon_id)[0]['moveId']
    print(egg_set)

    for group in mon_egg_group:
        egg_groups_list.extend(getPokemonIdsInEggGroup(int(group)))

    for move in egg_set:
        move_name = get_move_string(move)
        for mon in egg_groups_list:
            if mon in evolution_dex[str(pokemonID)]['path']:
                continue
            mon_learnset = get_mon_full_learnset(mon)
            baby_mon_id = evolution_dex[str(mon)]['path'][0]
            baby_mon_egg_set = get_egg_moves(baby_mon_id)[0]['moveId']
            pokemon_name = get_pokemon_name(mon)
            if mon_learnset == None:
                continue
            if move in mon_learnset['level']:
                egg_move_path[move_name].append([pokemon_name, "Level Up"])
            elif move in mon_learnset['tm']:
                egg_move_path[move_name].append([pokemon_name, "TM Move"])
            elif move in mon_learnset['tutor']:
                egg_move_path[move_name].append([pokemon_name, "Tutor"])
            elif move in baby_mon_egg_set:
                egg_move_path[move_name].append([pokemon_name, "Egg Move From Different Mon"])
    
    return egg_move_path

if __name__ != "__main__":
    full_data = load_data()
    personal_table = full_data['personal_table']['Personal']
    diff_forms, NAME_MAP = get_diff_form_dictionary()
    evolution_dex = full_data['evolution_dex']

if __name__ == "__main__":
    full_data = load_data()
    evolution_dex = full_data['evolution_dex']
    print(check_egg_moveset(246))
