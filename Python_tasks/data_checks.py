import copy
import time
from collections import defaultdict

import constants
from load_files import load_data, get_lumi_data
from pokemonUtils import (get_form_name, get_form_pokemon_personal_id,
                          get_pokemon_name, get_pokemon_name, get_diff_form_dictionary,
                          get_pokemon_id_from_name, get_mon_full_learnset)
from moveUtils import get_move_string, get_egg_moves_list
from eggGroups import getEggGroupViaPokemonId, getPokemonIdsInEggGroup, pokemonIdsByEggGroup, getEggGroupNameById

def get_average_time(execution_times_list):
    '''Do I really need to explain this one?'''
    return sum(execution_times_list) / len(execution_times_list)

def bad_encounter_data(pkmn_name, routeName=None, route=None):
    '''
    This is useful for checking whether there are bad encounters within the diff_forms
    '''
    bad_encounters = []
    if routeName == None and route == None:
        # print("This is an invalid pokemon in the dex:", pkmn_name)
        bad_encounters.append([pkmn_name, "Pokedex"])
        return bad_encounters
    print('BAD ENCOUNTER', pkmn_name, routeName, route)
    bad_encounters.append({pkmn_name, routeName, route})
    return bad_encounters

def is_valid_pokemon(pokemonId):
    return personal_table[pokemonId]['valid_flag']

def check_bad_encounter(encounters, tracker_route, lumi_formula_mon, temp_form_no, zoneID, method=''):
    '''
    This checks the methods that are on each route and verifies that no pokemon is missing
    '''
    name_routes = full_data['name_routes']

    bad_encounters = []
    if temp_form_no == constants.ENCOUNTER_VARIANT_JSON_HANDLER:
        temp_form_no = 0

    pokemonPersonalId = get_form_pokemon_personal_id(lumi_formula_mon, temp_form_no)
    is_valid = is_valid_pokemon(pokemonPersonalId)

    if pokemonPersonalId is not None and is_valid == 0:
        bad_encounter = bad_encounter_data(get_pokemon_name(pokemonPersonalId), name_routes[tracker_route], zoneID)
        bad_encounters.append(bad_encounter)
        return bad_encounters
    elif method == constants.TRACKER_METHOD:
        return -1
    else:
        return -2

def check_bad_dex_mon(pokemonID, invalid_pokemon):
    pokemonName = get_pokemon_name(pokemonID)
    is_valid = is_valid_pokemon(pokemonID)
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
            moved the 2nd slot mon to the 10th slot 
              (and deleted the pokemon that was in slot 10 before, same thing with the rest)
            moved the 5th slot mon to the 11th slot
            moved the 6th slot mon to the 12th slot
        For the radar and incense mons I did the following to the copy of the list:
            Changed the 2nd slot of the list to be the 4th slot of the radar
            Changed the 5th slot to be the 1st slot of the very first incense category 
              ('gbaRuby' unless there's something out of order).
            Changed the 6th slot to be the 2nd slot of the incense.
        Compared the contents of the two lists (original_list and copy_of_list) 
          to find if there were pokemon that were in the original_list 
          and not in the copy_of_list
        If there were pokemon that were in original_list and 
          not in the copy_of_list, a flag goes up and throws a warning.
    '''
    original_list = []
    missing_list = []
    incense_count = 0
    radar_list = {zoneID: []}

    # if constants.GAME_MODE == "vanilla":
        # We need to do something else...

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
        print("This route would have pokemon missing", radar_list)
    unique_list = list(set(missing_list))
    if len(unique_list) > 0:
        return (1, unique_list)
    return (-1, unique_list)

def bfs_egg_moves(pokemonList, move, current_path, original_pokemon, visited):
    new_egg_move_path = defaultdict(list)
    move_name = get_move_string(move)

    for pokemonID in pokemonList:
        if pokemonID == -1:
            break
        egg_move_check = check_for_all_egg_moves(new_egg_move_path[move_name])
        if egg_move_check[0] == 0:
            break
        egg_groups_list = []
        mon_egg_group = getEggGroupViaPokemonId(pokemonID)
        for group in mon_egg_group:
            if group == int(5) and move not in constants.SMEARGLE_NO_SKETCH_LIST:
                current_path.append(constants.SMEARGLE) # This is Smeargle
                egg_move_dict = find_egg_moveset_path(constants.SMEARGLE, move)
                egg_move_dict['Path'] = current_path
                new_egg_move_path[move_name].append(egg_move_dict)
                return new_egg_move_path[move_name]
            egg_groups_list.extend(getPokemonIdsInEggGroup(int(group)))
        for pokemon in egg_groups_list:
            if pokemon in evolution_dex[str(original_pokemon)]['path'] or pokemon in visited:
                continue
            is_valid = is_valid_pokemon(pokemon)
            if not is_valid:
                continue
            visited.add(pokemon)
            pokemon_name = get_pokemon_name(pokemon)

            # Create a separate copy of the current_path for each Pokémon
            current_path_copy = current_path.copy()
            if current_path_copy[0] != original_pokemon:
                current_path_copy.insert(0, original_pokemon)  # Add the initial pokemonID only if the list is empty
            current_path_copy.append(pokemonID)
            current_path_copy.append(pokemon)

            egg_move_dict = find_egg_moveset_path(pokemon, move)
            if egg_move_dict == -1:
                continue
            egg_move_dict['Path'] = current_path_copy
            new_egg_move_path[move_name].append(egg_move_dict)
            if egg_move_dict['Method'] != "Egg Move":
                continue
    egg_move_check = check_for_all_egg_moves(new_egg_move_path[move_name])
    if egg_move_check[0] == 0:
        return new_egg_move_path[move_name]
    if egg_move_check[0] == -1:
        return
    else:
        bfs_egg_moves(egg_move_check, move, current_path, original_pokemon, visited)

def check_for_all_egg_moves(egg_move_paths):
    if not egg_move_paths:  # Check if the array is empty
        return [-1]

    all_eggs = all(egg_move_dict['Method'] == 'Egg Move' for egg_move_dict in egg_move_paths)

    if all_eggs:
        egg_pokemon = [get_pokemon_id_from_name(egg_move_dict['Pokemon']) for egg_move_dict in egg_move_paths]
        return egg_pokemon
    else:
        non_egg_pokemon = [get_pokemon_id_from_name(egg_move_dict['Pokemon'])
                    for egg_move_dict in egg_move_paths
                    if egg_move_dict['Method'] != 'Egg Move']
        return [0, non_egg_pokemon]

def find_egg_moveset_path(pokemonID, move):
    if pokemonID == constants.SMEARGLE:
        return {'Pokemon': "Smeargle", 'Method': "Sketch that Bitch", 'Path': []}
    pokemon_name = get_pokemon_name(pokemonID, constants.GAME_MODE == constants.GAME_MODE_3)
    baby_mon_id = evolution_dex[str(pokemonID)]['path'][0]
    baby_mon_egg_set = get_egg_moves_list(baby_mon_id)
    pokemon_learnset = get_mon_full_learnset(pokemonID)
    egg_group_ids = getEggGroupViaPokemonId(pokemonID)
    egg_group_names = [getEggGroupNameById(egg_group_id) for egg_group_id in egg_group_ids]
    if pokemon_learnset is None:
        #This is for if the pokemon doesn't have a moveset according the the fullLearnset.json
        #AKA this pokemon is not currently valid
        return -1

    if move in pokemon_learnset['level']:
        return {
            'Pokemon': pokemon_name,
            'Egg Groups': egg_group_names,
            'Method': "Level Up",
            'Path': []
        }
    elif move in pokemon_learnset['tm']:
        return {
            'Pokemon': pokemon_name,
            'Egg Groups': egg_group_names,
            'Method': "TM Move",
            'Path': []
        }
    elif move in pokemon_learnset['tutor']:
        return {
            'Pokemon': pokemon_name,
            'Egg Groups': egg_group_names,
            'Method': "Tutor",
            'Path': []
        }
    elif move in baby_mon_egg_set:
        return {
            'Pokemon': pokemon_name,
            'Egg Groups': egg_group_names,
            'Method': "Egg Move",
            'Path': []
        }
    #Getting to the end here means that there wasn't a match for any move in the current mon's set
    return -1

def check_egg_moveset(pokemonID):
    egg_move_path = defaultdict(list)
    egg_groups_list = []

    mon_egg_group = getEggGroupViaPokemonId(pokemonID)
    baby_pokemon_id = evolution_dex[str(pokemonID)]['path'][0]
    egg_set = get_egg_moves_list(baby_pokemon_id)
    pokemon_name = get_pokemon_name(pokemonID)
    egg_group_names = [getEggGroupNameById(egg_group_id) for egg_group_id in mon_egg_group]

    for group in mon_egg_group:
        egg_groups_list.extend(getPokemonIdsInEggGroup(int(group)))

    for move in egg_set:
        move_name = get_move_string(move)
        if 5 in mon_egg_group and move not in constants.SMEARGLE_NO_SKETCH_LIST:
            egg_move_dict = find_egg_moveset_path(constants.SMEARGLE, move)
            egg_move_path[move_name].append(egg_move_dict)
            continue
        for mon in egg_groups_list:
            if mon in evolution_dex[str(pokemonID)]['path']:
                continue
            is_valid = is_valid_pokemon(mon)
            if not is_valid:
                continue
            egg_move_dict = find_egg_moveset_path(mon, move)
            if egg_move_dict == -1:
                continue
            egg_move_path[move_name].append(egg_move_dict)
        egg_move_check = check_for_all_egg_moves(egg_move_path[move_name])
        if egg_move_check[0] == 0:
            continue
        elif egg_move_check[0] == -1:
            print(f"Pokemon: {pokemon_name}", f"Egg Groups: {egg_group_names}", f"Move: {move_name} ({move})")
            continue
        else:
            # This means that egg_move_check is a list of mons 
            # and that all obtain the current move from egg moves
            shortest_egg_paths = bfs_egg_moves(egg_move_check, move, [egg_move_check[0]], pokemonID, set())
            if not shortest_egg_paths:
                break
            shortest_egg_path = shortest_egg_paths[-1]
            egg_move_path[move_name] = shortest_egg_path

    return egg_move_path


if __name__ != "__main__":
    full_data = load_data()
    personal_table = full_data['personal_table']['Personal']
    diff_forms, NAME_MAP = get_diff_form_dictionary()
    evolution_dex = full_data['evolution_dex']    