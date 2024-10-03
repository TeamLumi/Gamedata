import json
import os
import re
from operator import itemgetter
import time

import constants
from load_files import load_data
from data_checks import get_average_time

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
parent_file_path = os.path.abspath(os.path.dirname(__file__))
input_file_path = os.path.join(repo_file_path, constants.INPUT_NAME)
debug_file_path = os.path.join(parent_file_path, constants.DEBUG_NAME)

areas_file_path = os.path.join(input_file_path, 'areas_updated.csv')

scripts_file_path = os.path.join(repo_file_path, 'scriptdata')
bdsp_location_files_path = os.path.join(repo_file_path, 'placedatas')
bdsp_location_files = os.listdir(bdsp_location_files_path)

trainer_labels = 0
trainer_names = 0
areas = 0

first_excecution_time_list = []
second_execution_time_list = []

class UnsupportedTrainer(Exception):
    pass

class InvalidArg(Exception):
    pass

class MissingData(Exception):
    pass

class MultiTrainerError(Exception):
    pass

class SupportTrainerError(Exception):
    pass

with open(areas_file_path, encoding="utf-8") as f:
    areas = [line.strip().split(',') for line in f.readlines()]

def get_trainer_name(label_name):
    '''
    This takes the label of a trainer, matches it to the labelName in the trainer_names files and returns the trainerType
    '''
    label_data_array = trainer_names['labelDataArray']
    match = next((e for e in label_data_array if e['labelName'] == label_name), None)
    return match['wordDataArray'][0]['str'] if match else None

def get_trainer_id_from_partial(label_name):
    '''
    This is for finding the trainerID from a label name and matching it to the end of the labelName
    '''
    label_data_array = trainer_names['labelDataArray']
    for e in label_data_array:
        if e['labelName'].endswith(str(label_name.strip("'"))):
            return e['labelIndex']
    
    return special_trainer_names[label_name]

def get_trainer_label(label_name):
    label_data_array = trainer_labels['labelDataArray']
    match = next((e for e in label_data_array if e['labelName'] == label_name), None)
    return match['wordDataArray'][0]['str'] if match else None
    
def get_area_name(label_name):
    area_names = full_data['area_names']
    label_data_array = area_names['labelDataArray']
    match = next((e for e in label_data_array if e['labelName'] == label_name), None)
    return match['wordDataArray'][0]['str'] if match else None

def get_area_display_name(label_name):
    area_display_names = full_data['area_display_names']
    label_data_array = area_display_names['labelDataArray']
    match = next((e for e in label_data_array if e['labelName'] == label_name), None)
    return match['wordDataArray'][0]['str'] if match else None

def get_map_info(label_name):
    map_info = full_data['map_info']
    zone_data = map_info['ZoneData']
    match = next((e for e in zone_data if e['ZoneID'] == label_name), None)
    areaName = get_area_display_name(match['MSLabel']) if match and len(match['MSLabel']) > 0 else get_area_name(match['PokePlaceName'])
    return areaName, match['MSLabel']

def get_trainer_data_from_place_datas():
    '''
    This iterates through every placedata file and searches for any person that has a trainerID > 0
    If it is, then it passes that event data to the diff_trainer_data function
    '''
    trainers = []
    for bdsp_location_file in bdsp_location_files:
        with open(os.path.join(repo_file_path, 'placedatas', bdsp_location_file), 'r') as f:
            data = json.load(f)
        for event in data['Data']:
            trainerID = event['TrainerID']
            zoneID = event['zoneID']
            if trainerID > 0 and trainerID < 10000 and zoneID != -1:
                trainer = diff_trainer_data(event, None, None)
                trainers.append(trainer)
    return trainers

def generate_trainer_name(raw_trainer_name, pokemon1_level):
    level = int(pokemon1_level)
    if level is None:
        return None

    i1 = raw_trainer_name.find('[')
    i2 = raw_trainer_name.find(']')

    bad_section = raw_trainer_name[i1:i2+1]
    is_boss_trainer = (constants.CITY_TRAINER in bad_section or constants.LEAGUE_TRAINER in bad_section)
    if not is_boss_trainer or constants.MASTER_TRAINER in raw_trainer_name:
        return raw_trainer_name

    trainer_substring = raw_trainer_name[:i1-1] + raw_trainer_name[i2+1:]
    if level == 100:
        return trainer_substring + ' Rematch'
    return trainer_substring

def get_random_team_data(file_path, trainerID1, trainerID2, lookup, team_num):
    '''
    This is called in the get_assorted_trainer_data for any trainers that have randomized teams.
    Soooo many branching paths here @.@
    1. Master Type Trainers for Arceus Event
    2. Celebi event trainers (gym Leaders from Johto)
    3. Any Barry trainer that has randomized teams
    4. Every other single trainer battle that has randomized teams
    '''
    trainers = []
    zoneID, areaName = get_zone_info(file_path)

    def add_trainers(zoneID, trainer_ids, team_types=None, is_gym_rematch = 0):
        for trainer_id, team_type in zip(trainer_ids, team_types or []):
            trainer = get_single_trainer(zoneID, trainer_id, trainer_ids, team_type, is_gym_rematch)
            trainers.append(trainer)
        return trainers

    if constants.MASTER_TRAINER == lookup:
        temp_master_IDs = parse_randomized_teams(file_path, "", len(team_num), lookup)
        add_trainers(zoneID, temp_master_IDs, team_num)
        return trainers

    elif constants.CELEBI == lookup:
        temp_celebi_IDs = parse_randomized_teams(file_path, "", team_num, lookup)
        add_trainers(zoneID, temp_celebi_IDs, [lookup] * len(temp_celebi_IDs))
        return trainers
        
    elif constants.BARRY in lookup:
        temp_trainer_IDs = parse_randomized_teams(file_path, lookup, team_num, None)
        for ID in temp_trainer_IDs:
            team_type = lookup.split("_")[-1].strip('"')
            trainer = get_single_trainer(zoneID, ID, temp_trainer_IDs, team_type)
            trainers.append(trainer)
        return trainers
    else:
        temp_trainer_IDs = parse_randomized_teams(file_path, lookup, team_num, None)
        is_gym_rematch = 0
        if constants.REMATCH_SUBSTRING in lookup:
            is_gym_rematch = 1
        add_trainers(zoneID, temp_trainer_IDs, None, is_gym_rematch)
        for ID in temp_trainer_IDs:
            trainer = get_single_trainer(zoneID, ID, temp_trainer_IDs, None, is_gym_rematch)
            trainers.append(trainer)
        return trainers

def get_assorted_trainer_data(file_path, trainerID1, trainerID2, args):
    '''
    Refer to get_random_team_data for info about the branching paths here
    '''
    trainers = []
    zoneID, areaName = get_zone_info(file_path)
    for starter in constants.STARTERS:
        rival_lookup = f"ev_{areaName.lower()}_randomteam_barry_{starter}"
        rival_teams = get_random_team_data(file_path, trainerID1, trainerID2, rival_lookup, 4)
        trainers.extend(rival_teams)
    if rival_teams:
        return trainers
    if trainers == []:
        cyrus_lookup = f"ev_{areaName.lower()}_randomteam_cyrus"
        cyrus_teams = get_random_team_data(file_path, trainerID1, trainerID2, cyrus_lookup, 4)
        if cyrus_teams:
            trainers.extend(cyrus_teams)
            return trainers
    if trainers == []:
        master_teams = get_random_team_data(file_path, trainerID1, trainerID2, constants.MASTER_TRAINER, constants.MASTER_TRAINER_TYPES)
        if master_teams:
            trainers.extend(master_teams)
            return trainers
    if trainers == []:
        celebi_teams = get_random_team_data(file_path, trainerID1, trainerID2, constants.CELEBI, 7)
        if celebi_teams:
            trainers.extend(celebi_teams)
            return trainers
    for i in [constants.MALE, constants.FEMALE]:
        if i == constants.MALE:
            lucas_support_teams = get_support_trainers_data(file_path, areaName, constants.MALE, zoneID )
            if lucas_support_teams:
                trainers.extend(lucas_support_teams)
        dawn_support_teams = get_support_trainers_data(file_path, areaName, constants.FEMALE, zoneID )
        if dawn_support_teams:
            trainers.extend(dawn_support_teams)
            return trainers
    if trainers == []:
        print("Lucas and Dawn's Single Battles are not yet supported:", areaName, args)

def get_single_trainer(zoneID, ID, temp_IDs, name, is_gym_rematch=0):
    '''
    Branching paths are the result of get_random_team_data
    '''
    trainer = diff_trainer_data(None, zoneID, int(ID), is_gym_rematch)
    if name in constants.STARTERS:
        # This is for Rival Battles for right now, it may have Lucas/Dawn battles eventually?
        trainer["name"] = f"{trainer['name']} {name.capitalize()} Team {str(temp_IDs.index(ID) + 1)}"
        trainer['method'] = constants.SCRIPTED_METHOD
        trainer['format'] = constants.SINGLE_FORMAT
        return trainer
    elif name in constants.MASTER_TRAINER_TYPES:
        trainer["name"] = f"{name.capitalize()} Master Trainer {trainer['name']}"
        trainer['method'] = constants.SCRIPTED_METHOD
        trainer['format'] = constants.SINGLE_FORMAT
        return trainer
    elif name == constants.CELEBI:
        trainer['method'] = constants.SCRIPTED_METHOD
        trainer['format'] = constants.SINGLE_FORMAT
        return trainer
    elif len(temp_IDs) > 1:
        trainer["name"] = f"{trainer['name']} Team {str(temp_IDs.index(ID) + 1)}"
        trainer['method'] = constants.SCRIPTED_METHOD
        trainer['format'] = constants.SINGLE_FORMAT
        return trainer

    trainer["name"] = f"{trainer['name']}"
    trainer["format"] = constants.SINGLE_FORMAT
    trainer["link"] = ""

    return trainer

def get_trainer_data(zoneID, trainerID, method, is_gym_rematch=0):
    '''
    This is the core of getting trainer data for any trainer.
    This takes the trainerID and pulls data from each trainer file that is needed.
    It then checks if there is a trainer_label and trainer_name as a check for new trainers in the TrainerTable.json
    The zoneID is used to get the areaName (for the tracker) and the zoneName (for everything else)
    The areaName is a generalized name for the region the zoneID is in
    zoneName pulls from the areas_updated.csv which has the specific areas that are typically unique to the zoneID
    After these checks, the trainer info is created to be used everywhere else in the script
    '''
    TRAINER_TABLE = full_data['raw_trainer_data']
    trainer_data = TRAINER_TABLE['TrainerData'][trainerID]
    trainer_type = TRAINER_TABLE['TrainerType'][trainer_data['TypeID']]
    trainer_label = get_trainer_label(trainer_type['LabelTrType'])
    name_routes = full_data['name_routes']

    if not trainer_label:
        print("This trainer doesn't have a label in game:", trainer_type['LabelTrType'], trainerID)        
    trainer_name = get_trainer_name(trainer_data['NameLabel'])
    if not trainer_name:
        trainer_name = trainer_data['NameLabel'].split("_")[-1].capitalize()
        print("This trainer doesn't have a name in game:", trainer_data['NameLabel'], trainerID)
    areaName, _ = get_map_info(zoneID)
    zones = areas[zoneID + 1]
    zoneName = zones[3] if zones[3] != '' else zones[4]
    if zoneName == '':
        zoneName = areaName
    for name, route in name_routes.items():
        if areaName in route:
            areaName = name
    if areaName in constants.TRACKER_VARS.keys():
        areaName = constants.TRACKER_VARS.get(areaName, areaName)
    if not areaName.startswith("lmpt"):
        print(f"This areaName is not in line with the tracker standards: {areaName}")
    trainer = {
        'areaName': areaName,
        'zoneName': zoneName,
        'zoneId': int(zoneID),
        'trainerId': trainerID,
        'rematch': is_gym_rematch,
        'name': trainer_name,
        'type': trainer_label,
        'method': "",
        'format': "",
        'link': ""
    }
    return trainer

def parse_randomized_teams(file_path, lookup, count, type):
    '''
    count will be how many trainers are expected to be found
    lookup will be the randomteam that you are trying to find.
    it will always be in this format: ev_{LOCATION}_randomteam_{NAME of trainer} with optional _{STARTER Name} then _rematch
    i.e.:
    ev_c03gym0101_randomteam_roark
    ev_c03gym0101_randomteam_roark_rematch
    ev_c02_randomteam_barry_turtwig
    ev_c02_randomteam_barry_turtwig_rematch
    '''
    regex_lookup_dict = {
        constants.MASTER_TRAINER: constants.MASTER_TRAINER_LOOKUP,
        constants.CELEBI: constants.CELEBI_LOOKUP,
        constants.EVIL_TYPE: constants.EVIL_LOOKUP,
        None: constants.LDVAL_LOOKUP,
    }
    regex_lookup = regex_lookup_dict.get(type)
    trainers = []
    found_lookup = False
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            substrings = line.split('\n')
            for substring in substrings:
                is_rematch = True if constants.REMATCH_SUBSTRING in lookup and constants.REMATCH_SUBSTRING in substring else False
                if found_lookup and regex_lookup in substring:
                    match = re.split(constants.LDVAL_PATTERN, substring)[2]
                    if match:
                        trainer_id = match.strip("'")
                        trainers.append(trainer_id)
                        if len(trainers) == count:
                            return trainers
                elif not found_lookup and substring.startswith(lookup):
                    found_lookup = True
                elif not found_lookup and substring.startswith(lookup) and is_rematch:
                    found_lookup = True
    return trainers

def get_support_trainers_data(file_path, area_name, support_name, zoneID):
    """
    The purpose of this function is to get the support trainers data for Multi Battles and standard battles
    """
    def get_bad_support_IDs(support_name, file_path):
        '''
        The point of this is to have at least SOME Lucas/Dawn Battles rather than none
        Can probably be deleted and/or replaced after Scripting changes
        '''
        for support in [support_name]:
            if support == constants.MALE:
                temp_support_IDs = parse_randomized_teams(file_path, constants.BAD_SUPPORT_LOOKUP1, 3, None)
                return temp_support_IDs
            temp_support_IDs = parse_randomized_teams(file_path, constants.BAD_SUPPORT_LOOKUP2, 3, None)
            return temp_support_IDs

    trainers = []
    temp_support_IDs = []
    rival_multi_lookup = f"{area_name.lower()}_rival_support"

    current_support_lookup = f"{area_name.lower()}_{support_name}_100" ### This is for Lucas and Dawn in C01 and C07. Is this the most optimal? Maybe?
    temp_support_IDs = parse_randomized_teams(file_path, current_support_lookup, 3, None)
    if temp_support_IDs == [] and support_name != None:
        temp_support_IDs = get_bad_support_IDs(support_name, file_path)
    if (
        temp_support_IDs == [] 
        and support_name == constants.FEMALE 
        and area_name == constants.ROUTE_210
        ):
        temp_support_IDs = parse_randomized_teams(file_path, constants.R210B_BAD_SUPPORT_LOOKUP1, 3, None)
    elif (
        temp_support_IDs == [] 
        and support_name == constants.MALE 
        and area_name == constants.ROUTE_210
        ):
        temp_support_IDs = parse_randomized_teams(file_path, constants.R210B_BAD_SUPPORT_LOOKUP2, 3, None)        
    if (
        temp_support_IDs == [] 
        and support_name == constants.MALE 
        and area_name == constants.ROUTE_224
    ):
        temp_support_IDs = parse_randomized_teams(file_path, constants.R224_BAD_SUPPORT_LOOKUP2, 3, None)
    elif (
        temp_support_IDs == [] 
        and support_name == constants.FEMALE 
        and area_name == constants.ROUTE_224
        ):
        temp_support_IDs = parse_randomized_teams(file_path, constants.R224_BAD_SUPPORT_LOOKUP1, 3, None)
    if temp_support_IDs == []:
        temp_support_IDs = parse_randomized_teams(file_path, rival_multi_lookup, 3, None)
    if temp_support_IDs == []:
        print("Support Trainers still needs more work", area_name, zoneID)
        raise SupportTrainerError
    for ID in temp_support_IDs:
        trainer = get_trainer_data(zoneID, int(ID), constants.SCRIPTED_METHOD)
        trainer["method"] = constants.SCRIPTED_METHOD
        trainer["format"] = constants.MULTI_PARTNER_FORMAT
        trainer["link"] = constants.SUPPORT_LINK
        trainers.append(trainer)
    return trainers

def diff_trainer_data(event, zoneID, trainerID, is_gym_rematch=0):
    '''
    The event variable is for the place_datas function
    The zoneID and trainerID is for the ev_script function
    Make sure that when you call one or the other that the opposite variable(s) is(are) None
    i.e: diff_trainer_data(event, None, None) or diff_trainer_data(None, zoneID, trainerID)
    '''
    trainer = {}
    if event is not None:
        zoneID = int(event['zoneID'])
        trainerID = int(event['TrainerID'])
        trainer = get_trainer_data(zoneID, trainerID, constants.PLACE_DATA_METHOD)
        trainer['method'] = constants.PLACE_DATA_METHOD
        trainer['format'] = constants.SINGLE_FORMAT
        return trainer
    else:
        trainer = get_trainer_data(zoneID, trainerID, constants.SCRIPTED_METHOD, is_gym_rematch)
        trainer['method'] = constants.SCRIPTED_METHOD
        return trainer

def get_multi_trainers(trainerID1, trainerID2, zoneID, format):
    '''
    format can either be "Multi" or "Double" depending on which you choose
    '''
    trainers = []
    trainerID2_used = False

    for trainerID in [trainerID1, trainerID2]:
        trainer = diff_trainer_data(None, zoneID, int(trainerID))
        trainer["format"] = format
        if trainerID2_used == False or not trainerID2:
            trainer["link"] = trainerID2
            trainerID2_used = True
        else:
            trainer["link"] = trainerID1
        trainers.append(trainer)
    return trainers

def get_named_trainer_data(zoneID, trainerID1, trainerID2, args):
    '''
    This is for all the trainers that have names instead of trainerIDs
    An example is LASS01
    The first thing this checks is if there is a 2nd trainerID for multi/double battles
    Inside of each of these is a check for any trainerID above 651.
    If it is above 651, it pulls the trainer name from the trainer enum obtained from @Sma
    '''
    trainerID1 = trainerID1.strip("'")
    trainers = []
    special_trainer_names = full_data['special_trainer_names']
    if len(trainerID2) > 0:
        trainerID2 = trainerID2.strip("'")
        temp_trainerID1 = get_trainer_id_from_partial(trainerID1)
        temp_trainerID2 = get_trainer_id_from_partial(trainerID2)
        if temp_trainerID1 > 651 or temp_trainerID2 > 651:
            temp_trainerID1 = special_trainer_names[trainerID1.strip("'")]
            temp_trainerID2 = special_trainer_names[trainerID2.strip("'")]            
            
        trainer1, trainer2 = get_multi_trainers(temp_trainerID1, temp_trainerID2, zoneID, constants.DOUBLE_FORMAT)
        trainers.append(trainer1)
        trainers.append(trainer2)
        return trainers

    temp_trainerID1 = get_trainer_id_from_partial(trainerID1)
    if temp_trainerID1 > 651:
        # There is a discrepancy in the data with the trainer labels and named trainers
        # This only happens after TID 651
        # If it is above 651, it pulls from the trainer enums obtained from @Sma
        temp_trainerID1 = special_trainer_names[trainerID1.strip("'")]

    trainer = diff_trainer_data(None, zoneID, int(temp_trainerID1))
    trainer["format"] = constants.SINGLE_FORMAT
    trainer["link"] = ""
    trainers.append(trainer)
    if trainers == []:
        print("There's something wrong with the Named Trainer Data!!")
    return trainers

def get_multi_trainer_data(file_path, trainerID1, trainerID2, trainerID3, substring):
    '''
    This is for Multi Trainer Battles.
    It operates the same way as the other files except there is a third trainerID.
    Something to note in the format the multi_trainer_battles are called:
    The support trainer is in the first slot, 
    The left enemy trainer is in the 2nd slot
    The right enemy trainer is in the 3rd slot
    '''

    def get_multi_support_trainers(file_path, areaName, zoneID):
        return [
            *get_support_trainers_data(file_path, areaName, constants.MALE, zoneID),
            *get_support_trainers_data(file_path, areaName, constants.FEMALE, zoneID),
        ]

    trainers = []
    zoneID, areaName = get_zone_info(file_path)
    if trainerID3.isnumeric():
        # This is for if the trainerID is just the number like 751
        trainer2, trainer3 = get_multi_trainers(trainerID2, trainerID3, zoneID, constants.MULTI_FORMAT)
        trainers.extend([
            trainer2,
            trainer3,
            *get_multi_support_trainers(file_path, areaName, zoneID),
        ])
        return trainers
    elif trainerID3[0] == "@":
        # This is for the trainers that are defined previously in the function
        trainers.extend(get_multi_support_trainers(file_path, areaName, zoneID))
        team_galactic_lookup = f"pos_{areaName.lower()}_gingakanbu"

        temp_enemy_IDs = parse_randomized_teams(file_path, team_galactic_lookup, 2, constants.EVIL_TYPE)
        if temp_enemy_IDs:
            trainerID2 = temp_enemy_IDs[0]
            trainerID3 = temp_enemy_IDs[1]
            trainer2, trainer3 = get_multi_trainers(trainerID2, trainerID3, zoneID, constants.MULTI_FORMAT)
            trainers.append(trainer2)
            trainers.append(trainer3)
            return trainers
        else:
            print("Unable to find Multi Trainer (variable) opponent teams", areaName, substring)
            raise MultiTrainerError
    else:
        print("Unable to get enough trainers for Multi Trainers here:", areaName, substring)
        raise MultiTrainerError

def get_temp_var_trainer_data(file_path, trainerID1, trainerID2, args):
    '''
    This is when the trainerID starts with @.
    This covers 2 situations:
        1. Any fight that has been randomized (i.e. Gym Leaders, E4 Members)
        2. Every other fight with temp variables. Check the get_random_team_data
    '''

    trainers = []
    zoneID, areaName = get_zone_info(file_path)
    gym_leader_lookup = f"ev_{areaName.lower()}_randomteam"
    if constants.GYM_AREA_NAME in areaName:
        gym_leaders = get_random_team_data(file_path, trainerID1, trainerID2, gym_leader_lookup, 4)
        trainers.extend(gym_leaders)

        gym_leader_rematch_lookup = f"ev_{areaName.lower()}_randomteam_{constants.GYM_LEADER_LOOKUP[areaName.lower()]}_rematch"
        rematch_gym_leaders = get_random_team_data(file_path, trainerID1, trainerID2, gym_leader_rematch_lookup, 4)
        trainers.extend(rematch_gym_leaders)
        return trainers
    elif constants.E4_AREA_NAME in areaName and constants.ROOM_AREA_NAME not in areaName:
        e4_trainers = get_random_team_data(file_path, trainerID1, trainerID2, gym_leader_lookup, 4)
        trainers.extend(e4_trainers)

        e4_trainers_lookup = f"ev_{areaName.lower()}_randomteam_{constants.GYM_LEADER_LOOKUP[areaName.lower()]}_rematch"
        rematch_e4_trainers = get_random_team_data(file_path, trainerID1, trainerID2, e4_trainers_lookup, 4)
        trainers.extend(rematch_e4_trainers)
        return trainers
    assorted_trainers = get_assorted_trainer_data(file_path, trainerID1, trainerID2, args)
    trainers.extend(assorted_trainers)
    return trainers

def get_standard_trainer_data(trainerID1, trainerID2, zoneID):
    '''
    This is for standard trainers that only have their trainerIDs in the trainer battle calls
    '''
    trainers = []
    if trainerID2.isnumeric():
        trainer1, trainer2 = get_multi_trainers(trainerID1, trainerID2, zoneID, constants.DOUBLE_FORMAT)
        trainers.append(trainer1)
        trainers.append(trainer2)
        return trainers
    trainer = diff_trainer_data(None, zoneID, int(trainerID1))
    trainer["format"] = constants.SINGLE_FORMAT
    trainer["link"] = ""
    trainers.append(trainer)
    return trainers

def get_all_trainer_data(file_path, args, substring):
    '''
    This is the root function that branches to get all trainer's data
    Multi Battles are checked to see if the trainerID3 is > 0
    Standard trainers are check to see if the trainerID is just a number
    Temporary trainers are called if the trainerID starts with an "@"
    Named Trainers are called last if the trainerID is anything like LASS01 or similar
    '''
    trainers = []
    trainerID1 = args[0]
    trainerID2, trainerID3 = "", ""
    if len(args) >= 2:
        trainerID2 = args[1].strip()
    if len(args) > 2:
        trainerID3 = args[2].strip()
    zoneID, areaName = get_zone_info(file_path)

    ### Multi trainer data here
    if len(trainerID3) > 0:
        trainers.extend(get_multi_trainer_data(file_path, trainerID1, trainerID2, trainerID3, substring))
        return trainers

    # This second section is for if the trainerID is bog standard just calling a number from the TTable
    elif trainerID1.isnumeric():
        trainers.extend(get_standard_trainer_data(trainerID1, trainerID2, zoneID))
        return trainers
    # This next section is for the temp variables that are called like @SCWK_TEMP3
    elif trainerID1[0] == "@":
        trainers.extend(get_temp_var_trainer_data(file_path, trainerID1, trainerID2, args))
        return trainers
    # This last section is for the trainers that are called by name in the scripts like BATTLEG_01 or something like that.
    elif not trainerID1.isnumeric():
        trainers.extend(get_named_trainer_data(zoneID, trainerID1, trainerID2, args))
        return trainers
    else:
        print("There is Missing Data here:", areaName, trainerID1, trainerID2)
        raise MissingData

def parse_trainer_btl_set(substring):
    '''
    This is the regex function that splits the _TRAINER_BTL_SET or _TRAINER_MULTI_BTL_SET into it's separate parts
    2 or 3 parts respectively
    '''
    match = re.search(constants.TRAINER_PATTERN, substring)
    match2 = re.split(constants.MULTI_TRAINER_PATTERN, substring)
    if match:
        arg1, arg2 = match.groups()
        if len(arg2) > 1:
            args = [arg1.strip("'"), arg2.strip("'")]
            return args
        return[arg1]
    elif constants.MORIMOTO in substring:
        return [constants.MORIMOTO]
    elif match2:
        arg1 = match2[1].split(",")[0].strip("'")
        arg2 = match2[1].split(",")[1].strip("'")
        arg3 = match2[1].split(",")[2].strip("'")
        args = [arg1, arg2, arg3]
        return args
    else:
        return substring

def create_zone_id_map():
    '''
    This creates a {zone_name: zone_id} dictionary using the areas_updated.csv
    '''
    zone_dict = {}
    reverse_zone_dict = {}
    for place in areas:
        zone_index = int(areas.index(place) - 1)
        zone_name = areas[zone_index][-1]
        zone_id = areas[zone_index][0]
        zone_dict[zone_name] = zone_id
        reverse_zone_dict[zone_id] = zone_name
    return zone_dict, reverse_zone_dict

def get_zone_info(file_path):
    '''
    This takes the zone_id_map that has been created and the filepath of the ev file
    It then returns the zone_id and zone_name if there is a match in the zone_dict keys
    If not, it errors with -1 and the zone_name to track down the culprit
    '''
    zone_name = separate_area_name(file_path)
    if zone_name == constants.EVE_AREA_NAME:
        return 446, zone_name # This is the zoneID for Solaceon Town
    if zone_name == constants.SUPPORT_AREA_NAME:
        return 429, zone_name # This is the zoneID for Sandgem Town
    if zone_name in zone_dict.keys():
        return int(zone_dict[zone_name]), zone_name
    else:
        return -1, zone_name

def separate_area_name(file_path):
    # Takes the full filepath of the ev file and splits it to return just the areaName
    return file_path.split("/")[-1].split(".")[0].upper()

def parse_ev_script_file(file_path):
    """
    The purpose of this function is to parse an ev file
    This finds every instance of the substring _TRAINER_BTL_SET or _TRAINER_MULTI_BTL_SET.
    """
    trainers = []
    zoneID, areaName = get_zone_info(file_path)

    if zoneID < 0:
        raise UnsupportedTrainer
    if areaName.startswith(constants.SHINING_PEARL_FILE_PREFIX):
        raise UnsupportedTrainer
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            substrings = line.split('\n')
            for substring in substrings:
                if constants.TRAINER_BATTLE in substring or constants.MULTI_TRAINER_BATTLE in substring:
                    args = parse_trainer_btl_set(substring.strip())
                else:
                    continue

                if substring in args:
                    print("There is something wrong with the args from this area", zoneID, areaName, args[0])
                    raise InvalidArg
                if zoneID != -1:
                    trainers.extend(get_all_trainer_data(file_path, args, substring))

    return trainers

def process_files(folder_path, callback):
    """
    Calls the provided callback function on every file in the specified folder.
    
    :param folder_path: The path to the folder containing the files to be processed.
    :param callback: A function that takes a file path as its only argument and performs some action on it.
    """
    trainers_list = []
    trainers = []
    trainers_set = set()
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if constants.PEARL_SPEAR_PILLAR in filename:
            continue
        try:
            trainers = callback(file_path)
        except (FileNotFoundError, IsADirectoryError):
            print(f"{file_path} is not a valid file path or does not exist")
            return
        except (MissingData, SupportTrainerError):
            print(file_path)
            return
        except UnsupportedTrainer:
            continue
        trainers_set.update([frozenset(d.items()) for d in trainers])
    trainers_list = [dict(s) for s in trainers_set]

    trainer_data = get_trainer_data_from_place_datas()
    for battle in trainers_list:
        ordered_battle = {key: battle[key] for key in constants.DESIRED_ORDER}
        trainer_data.append(ordered_battle)
    sorted_data = sorted(trainer_data, key=itemgetter('zoneId', 'trainerId'))
    with open(os.path.join(debug_file_path, 'trainer_info.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, indent=2)
    return sorted_data

if __name__ != "__main__":
    full_data = load_data()
    zone_dict, reverse_zone_dict = create_zone_id_map()
    trainer_labels = full_data['trainer_labels']
    trainer_names = full_data['trainer_names']
    special_trainer_names = full_data['special_trainer_names']
