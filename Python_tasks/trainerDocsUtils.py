import json
import math
import os
import re
import time

import constants
from convert_lmpt_data import getTrainerData, find_zone_id
from data_checks import get_average_time
from load_files import load_data
from pokemonUtils import get_pokemon_from_trainer_info, get_pokemon_name
from trainerUtils import parse_ev_script_file, process_files, get_map_info, get_area_display_name

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
output_file_path = os.path.join(repo_file_path, "Python_tasks", constants.OUTPUT_NAME)
trainer_doc_data_file_path = os.path.join(repo_file_path, constants.TRAINER_DOC_PATH, "trainer_doc_output.txt")

first_excecution_time_list = []
second_execution_time_list = []

def get_trainer_pokemon(trainerId, output_format):
    '''
    Using the get_pokemon_from_trainer_info from pokemonUtils
    Requires the trainerId and the output_format being either "Scripted" or "Place Data"
    Those are referenced in Constants.py
    '''
    TRAINER_TABLE = full_data['raw_trainer_data']

    pokemon_list = []
    trainer = None
    for t in TRAINER_TABLE["TrainerPoke"]:
        if t["ID"] == trainerId:
            trainer = t
            break
    pokemon_list = get_pokemon_from_trainer_info(trainer, output_format)

    return pokemon_list

def sort_dicts_by_key(dicts_list, sort_key1, sort_key2, sort_key1_order):
    """
    Sorts a list of dictionaries by two given keys in ascending order
    The sorting order of the first key is specified by DOCS_ZONE_ORDER in Constants.py
    """
    return sorted(dicts_list, key=lambda x: (sort_key1_order.index(x[sort_key1]), x[sort_key2]))

def get_avg_trainer_level(trainer_team):
    '''
    Requires the full trainer's team
    This function counts the mons, add the levels of those mons together and returns the average
    '''
    mon_count = len(trainer_team)
    if len(trainer_team) == 0:
        print("Trainer does not have a team")
        return 0
    total_levels = 0
    for mon in trainer_team:
        total_levels += mon['level']
    trainer_avg = math.ceil(total_levels / mon_count)
    return trainer_avg

def sort_trainers_by_level(trainer_info):
    '''
    Requires the trainer_info from the process_files function or trainer_info.json
    Adds the trainer's team and average level to trainer_info
    Calls the sort_dicts_by_key function and sorts the trainers by zoneName then average level
    '''
    for trainer in trainer_info:
        trainerId = trainer['trainerId']
        trainer['team'] = get_trainer_pokemon(trainerId, constants.DOCS_METHOD)
        trainer['avg_lvl'] = get_avg_trainer_level(trainer['team'])
    sorted_trainers_by_level = sort_dicts_by_key(trainer_info, 'zoneName', 'avg_lvl', constants.DOCS_ZONE_ORDER)
    return sorted_trainers_by_level

def sort_trainers_by_route(trainer_info):
    '''
    Requires the trainer_info from the process_files function or trainer_info.json
    Calls the sort_dicts_by_key function and sorts the trainers by zoneName then trainerId
    Adds the trainer's team to trainer_info
    Adds each trainer to an `areaName: trainer_info` dictionary for use later
    '''
    sorted_trainers_by_key = sort_dicts_by_key(trainer_info, 'zoneName', 'trainerId', constants.DOCS_ZONE_ORDER)
    sorted_trainers_by_route = {}
    for trainer in sorted_trainers_by_key:
        areaName = trainer['areaName']
        trainerId = trainer['trainerId']
        trainer['team'] = get_trainer_pokemon(trainerId, constants.TRACKER_METHOD)
        if areaName not in sorted_trainers_by_route.keys():
            sorted_trainers_by_route[areaName] = [trainer]
        else:
            sorted_trainers_by_route[areaName].append(trainer)
    return sorted_trainers_by_route

def get_trainer_name(trainer_name, zone_name, TRAINER_INDEX=0, rematch=0):
    '''
    Requires trainer's name, zone name with optional trainer index
    Finds if there is team already in the trainer's name and adds zone_name in the middle
    If there is a TRAINER_INDEX, then it adds that value to the end of the name
    If there isn't any of those, it returns the trainer name with zone name
    '''
    if re.findall(constants.TEAM_REGEX, trainer_name):
        split_name = trainer_name.split()
        altered_trainer_name = ' '.join(split_name[:-2])
        if rematch == 1:
            altered_trainer_name += ' Rematch'
        team_name = ' '.join(split_name[-2:])
        updated_name = f"{altered_trainer_name} ({zone_name}) [{team_name}]"
        return [trainer_name, updated_name]
    if TRAINER_INDEX != 0:
        if rematch == 1:
            trainer_name += ' Rematch'
        updated_name = f"{trainer_name} {TRAINER_INDEX} ({zone_name})"
        name = f"{trainer_name} {TRAINER_INDEX}"
        return [name, updated_name]
    if rematch == 1:
        trainer_name += ' Rematch'
    updated_name = f"{trainer_name} ({zone_name})"
    return [trainer_name, updated_name]

def get_trainer_doc_moves(moves, index):
    '''
    Requires the full list of moves per pokemon and the index of each move
    '''
    if index < len(moves):
        return f"{moves[index]}\n"
    return f"(No Move)\n"

def write_trainer_docs_team_format(pokemon):
    '''
    Requires each pokemon from a trainer's team in write_to_trainer_docs_file function
    Returns the format for the header, ivs and evs of each pokemon
    '''
    pokemon_header = f"\n{get_pokemon_name(pokemon['id'])}\n{pokemon['level']}\n{pokemon['nature']}\n{pokemon['ability']}\n\n{pokemon['item']}\n"
    pokemon_ivs = f"{pokemon['ivhp']}/{pokemon['ivatk']}/{pokemon['ivdef']}/{pokemon['ivspatk']}/{pokemon['ivspdef']}/{pokemon['ivspeed']}\n"
    pokemon_evs = f"{pokemon['evhp']}/{pokemon['evatk']}/{pokemon['evdef']}/{pokemon['evspatk']}/{pokemon['evspdef']}/{pokemon['evspeed']}\n"

    return pokemon_header, pokemon_ivs, pokemon_evs

def write_to_trainer_docs_file(trainer, trainer_name):
    '''
    Requires the trainer info and trainer's full name from get_trainer_name
    Writes lines to trainer_doc_output.txt for Solarnce to c/p into the Trainer Docs Google Sheet
    '''
    trainerId = trainer['trainerId']
    rematch = trainer['rematch']
    battle_format = f"Format: {trainer['format']}"
    link = trainer['link']
    team = trainer['team']
    level_cap = "Level Cap:"
    if rematch == 1:
        trainer_name += " Rematch"
    with open(trainer_doc_data_file_path, "a") as f:
        f.write(f"{trainerId}\n{trainer_name}\n{level_cap}\n{battle_format}\n")
        for mon in team:
            mon_header, mon_ivs, mon_evs = write_trainer_docs_team_format(mon)
            moves = mon['moves']

            f.write(mon_header)
            for index in range(0, 4):
                f.write(get_trainer_doc_moves(moves, index))
            f.write(mon_ivs)
            f.write(mon_evs)
        if link != '':
            f.write(f"Paired with {link}\n\n")
        else:
            f.write(f"{link}\n\n")

def write_trainer_docs(trainer_list):
    '''
    Requires the full list of trainers from trainer_info.json or process_files
    This opens the trainer_doc_output.txt and deletes anything there first.
    This will then write every trainer to the trainer_doc_output.txt
    '''
    with open(trainer_doc_data_file_path, "w") as f:
        f.write("Trainer Documentation\n")
    for trainer in trainer_list:

        zone_name = trainer['zoneName']
        name = f"{trainer['type']} {trainer['name']}"
        full_trainer_name = get_trainer_name(name, zone_name)[0]

        write_to_trainer_docs_file(trainer, full_trainer_name)

def generate_repeat_trainer_name(trainer, index_dict):
    zone_name = f"{trainer['zoneName']} Trainers"
    name = f"{trainer['type']} {trainer['name']}"

    if constants.REPEAT_TRAINERS_LIST[0] in name:
        index_dict['Grunt'] += 1
        return get_trainer_name(name, zone_name, index_dict['Grunt'])
    elif constants.REPEAT_TRAINERS_LIST[1] in name:
        if index_dict['Lucas'] < 3:
            STARTER_INDEX = constants.STARTERS[index_dict['Lucas']].capitalize()
        else:
            STARTER_INDEX = f"End Game {constants.STARTERS[index_dict['Lucas'] - 3].capitalize()}"
        index_dict['Lucas'] += 1
        return get_trainer_name(name, zone_name, STARTER_INDEX)
    elif constants.REPEAT_TRAINERS_LIST[2] in name:
        if index_dict['Dawn'] < 3:
            STARTER_INDEX = constants.STARTERS[index_dict['Dawn']].capitalize()
        else:
            STARTER_INDEX = f"End Game {constants.STARTERS[index_dict['Dawn'] - 3].capitalize()}"
        index_dict['Dawn'] += 1
        return get_trainer_name(name, zone_name, STARTER_INDEX)
    elif constants.REPEAT_TRAINERS_LIST[3] in name:
        if index_dict['Barry'] < 3:
            STARTER_INDEX = constants.STARTERS[index_dict['Barry']].capitalize()
        else:
            STARTER_INDEX = f"End Game {constants.STARTERS[index_dict['Barry'] - 3].capitalize()}"
        index_dict['Barry'] += 1
        return get_trainer_name(name, zone_name, STARTER_INDEX)

def write_tracker_docs(trainers_list):
    '''
    Requires the trainers sorted for the Nuzlocke Tracker
    This formats all of the trainers for use in the Tracker
    '''
    all_trainers = []

    for zone in trainers_list.keys():
        zone_trainers = []
        index_dict = {
            "Grunt": 0,
            "Lucas": 0,
            "Dawn": 0,
            "Barry": 0,
        }
        for trainer in trainers_list[zone]:
            zone_trainer = {}
            zone_name = f"{trainer['zoneName']} Trainers"
            zone_id = trainer['zoneId']
            person_name = trainer['name']
            if person_name == constants.CEDRIC:
                trainer['name'] = constants.BARRY.capitalize()
            name = f"{trainer['type']} {trainer['name']}"
            rematch = trainer['rematch']
            is_repeat_trainer = any(substring in name for substring in constants.REPEAT_TRAINERS_LIST) and not re.findall(constants.TEAM_REGEX, name)
            if is_repeat_trainer:
                full_trainer_name = generate_repeat_trainer_name(trainer, index_dict)
            else:
                full_trainer_name = get_trainer_name(name, zone_name, 0, rematch)
            trainer_name = full_trainer_name[0]
            team_name = full_trainer_name[1]
            trainer_team = trainer['team']
            trainer_type = trainer['format']
            zone_trainer = {
                "content": trainer_team,
                "game": team_name,
                "name": trainer_name,
                "type": "Trainer",
                "route": zone_name,
                "zoneId": zone_id,
                "trainerType": trainer_type
            }
            zone_trainers.append(zone_trainer)
        all_trainers.append(zone_trainers)
    return all_trainers

def write_mapper_docs(trainers_list):
    '''
    Requires the trainers sorted for the Nuzlocke Tracker
    This formats all of the trainers for use in the Tracker
    '''
    all_trainers = {}

    for zone in trainers_list.keys():
        index_dict = {
            "Grunt": 0,
            "Lucas": 0,
            "Dawn": 0,
            "Barry": 0,
        }
        for trainer in trainers_list[zone]:
            zone_trainer = {}
            zone_name = trainer['zoneName']
            zone_id = trainer['zoneId']
            name = f"{trainer['type']} {trainer['name']}"
            rematch = trainer['rematch']
            is_repeat_trainer = any(substring in name for substring in constants.REPEAT_TRAINERS_LIST) and not re.findall(constants.TEAM_REGEX, name)
            if is_repeat_trainer:
                full_trainer_name = generate_repeat_trainer_name(trainer, index_dict)
            else:
                full_trainer_name = get_trainer_name(name, zone_name, 0, rematch)
            trainer_name = full_trainer_name[0]
            team_name = full_trainer_name[1]
            trainer_team = trainer['team']
            trainer_type = trainer['format']
            zone_trainer = {
                "team": trainer_team,
                "team_name": team_name,
                "name": trainer_name,
                "route": zone_name,
                "zoneId": zone_id,
                "trainerType": trainer_type,
                "trainer_id": trainer["trainerId"]
            }
            if zone_id not in constants.EXCLUSIVE_ZONE_IDS:
                areaName, _ = get_map_info(zone_id)
                generalized_zone_id = find_zone_id(areaName)
                if generalized_zone_id not in all_trainers.keys():
                    all_trainers[generalized_zone_id] = [zone_trainer]
                else:
                    all_trainers[generalized_zone_id].append(zone_trainer)
            else:
                if zone_id not in all_trainers.keys():
                    all_trainers[zone_id] = [zone_trainer]
                else:
                    all_trainers[zone_id].append(zone_trainer)

    return all_trainers

def get_trainer_doc_data():
    '''
    This gets the trainer documentation for Solarnce's Trainer Docs in the Google Sheets
    '''
    trainer_info = process_files(os.path.join(repo_file_path, constants.SCRIPT_DATA), parse_ev_script_file)
    print("Start trainer sorting by level")
    sorted_trainers = sort_trainers_by_level(trainer_info)
    print("Trainers have been sorted")
    write_trainer_docs(sorted_trainers)
    print("Done")

def get_tracker_trainer_data():
    '''
    This gets all of the trainer data for the tracker sorted by routes
    '''
    gym_leader_data = full_data['gym_leaders']

    original_teams = getTrainerData(gym_leader_data)
    trainer_info = process_files(os.path.join(repo_file_path, constants.SCRIPT_DATA), parse_ev_script_file)

    print("Start sorting trainers by zone")
    sorted_tracker_trainers = sort_trainers_by_route(trainer_info)
    print("Trainers have been sorted")
    new_trainers = write_tracker_docs(sorted_tracker_trainers)
    mapper_trainers = write_mapper_docs(sorted_tracker_trainers)
    for route in new_trainers:
        original_teams["1"].append(route)
    with open(os.path.join(output_file_path, 'Trainer_output.json'), 'w', encoding='utf-8') as f:
        json.dump(original_teams, f, indent=2)
    with open(os.path.join(output_file_path, "Mapper_Trainer_Output.json"), "w", encoding='utf-8') as f:
        json.dump(mapper_trainers, f, indent=2)

if __name__ == "__main__":
    start_time = time.time()
    full_data = load_data()
    get_trainer_doc_data()
    get_tracker_trainer_data()
    end_time = time.time()
    print("This is how long it took to run this file:", end_time - start_time, "seconds")
