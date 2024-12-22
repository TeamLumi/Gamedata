import json
import os
import re
import unicodedata
from collections import defaultdict

import constants
from load_files import load_data
from pokemonTypes import get_type_name
from evolutionUtils import get_first_evo_pokemon_id

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, constants.INPUT_NAME)
debug_file_path = os.path.join(parent_file_path, "Python_tasks", constants.DEBUG_NAME)
personal_data_path = os.path.join(input_file_path, 'PersonalTable.json')

move_enum = 0
FORM_MAP = {}
_move_properties_cache = {}  # cache for move properties

with open(personal_data_path, mode='r', encoding="utf-8") as f:
    personal_data = json.load(f)
    for curr in personal_data['Personal']:
        if curr['monsno'] not in FORM_MAP:
            FORM_MAP[curr['monsno']] = []
        FORM_MAP[curr['monsno']].append(curr['id'])

with open(os.path.join(input_file_path, 'moves.txt'), encoding="utf-8") as f:
    move_enum = [line.strip() for line in f if line.strip()]

def get_pokemon_form_id(monsno=0, id_=0):
    """
    BDSP does not view Pokemon in a format such as "MonsNo 3, Form 2".
    In order to get such a list for easier reasoning, one must generate it.
    That is what FORM_MAP does, and we should use it across all the util functions. 

    MonsNo (int): [form0 (Vanilla, ie. Bulbasaur), form1, ...]
    """
    return FORM_MAP[monsno].index(id_)

def get_move_properties(move_id=0):
    """
    If you ever need the properties of a move to be displayed, you can acquire all the data here.
    Just provide the move_id as an int
    """
    moves_namedata = full_data['moves_namedata']
    MovesTable = full_data['moves_table']

    move = MovesTable['Waza'][move_id]
    type_ = get_type_name(move['type'])
    damage_type = move['damageType']
    power = move['power']
    hit_per = move['hitPer']
    base_pp = move.get('basePP', 0)
    max_pp = int(base_pp * (8 / 5))

    name_data = moves_namedata['labelDataArray'][move_id]['wordDataArray']
    name = name_data[0]['str'] if name_data else 'None'
    desc = get_move_description(move_id)

    return {
        'name': name,
        'desc': desc,
        'type': type_,
        'damageType': damage_type,
        'maxPP': max_pp,
        'power': power,
        'accuracy': hit_per,
    }

def get_move_description(move_id=0):
    """
    Returns the in-game description of a move.
    """
    move_info_data = full_data['move_info']
    word_data = move_info_data['labelDataArray'][move_id]['wordDataArray']
    description = ' '.join(wd['str'] for wd in word_data)
    return description

def get_tm_compatibility(pokemon_id=0):
    if pokemon_id == 0:
        return None
    personal_data = full_data['personal_table']['Personal'][pokemon_id]
    machine_nos = [personal_data['machine1'], personal_data['machine2'], personal_data['machine3'], personal_data['machine4']]
    tm_binary_list = convert_list_to_binary_array(machine_nos)
    tm_compatibility = create_move_id_learnset(tm_binary_list)

    return tm_compatibility

def get_relumi_tm_compatibility(monsNo, formNo):
    ## This function is to get 3.0 datasets
    ## It needs to be a separate function becuase in this file you can't swap from monsNo and formNo to pokemonId
    if monsNo == 0:
        return None
    tm_data = full_data['tm_learnsets'][f"monsno_{monsNo}_formno_{formNo}"]
    machine_nos = [
        tm_data['set01'],
        tm_data['set02'],
        tm_data['set03'],
        tm_data['set04'],
        tm_data['set05'],
        tm_data['set06'],
        tm_data['set07'],
        tm_data['set08']
    ]
    tm_binary_list = convert_list_to_binary_array(machine_nos)
    tm_compatibility = create_move_id_learnset(tm_binary_list)

    return tm_compatibility

def decimal_to_binary_array(decimal_number):
    if not isinstance(decimal_number, int) or decimal_number < 0:
        raise ValueError("Input must be a non-negative integer")

    binary_string = bin(decimal_number)[2:]  # Convert to binary and remove the '0b' prefix
    binary_array = [int(bit) for bit in binary_string]

    # Pad the binary array to have a length of 32 by adding leading zeros
    binary_array = [0] * (32 - len(binary_array)) + binary_array

    return binary_array[::-1]

def convert_list_to_binary_array(decimal_list):
    if len(decimal_list) != 4 and len(decimal_list) != 8:
        raise ValueError("Input list must have exactly 4 or 8 elements")

    binary_array = []

    for decimal_number in decimal_list:
        if not isinstance(decimal_number, int) or decimal_number < 0:
            raise ValueError("All elements in the list must be non-negative integers")

        binary_array.extend(decimal_to_binary_array(decimal_number))

    # Pad the binary array to have a length of 128 by adding leading zeros
    binary_array = [0] * (128 - len(binary_array)) + binary_array

    return binary_array

def convert_to_32_bit_integers(binary_array):
    if len(binary_array) != 256:
        raise ValueError("Input array must have a length of 256")

    integers = []

    for i in range(0, 256, 32):
        integer_slice = binary_array[i:i+32]
        reversed_slice = integer_slice[::-1]
        integer_value = 0

        for bit in reversed_slice:
            integer_value = (integer_value << 1) | bit

        integers.append(integer_value)

    return integers

def get_tech_machine_learnset(pokemon_id=0):
    learnset = get_tm_compatibility(pokemon_id)
    MAX_TM_COUNT = 104
    if learnset == None:
        return []
    can_learn = []
    for move in learnset:
        can_learn.append({'level': 'tm', 'moveId': move})

    return can_learn

def get_relumi_tm_learnset(monsNo=0, formNo=0):
    learnset = get_relumi_tm_compatibility(monsNo, formNo)
    if learnset == None:
        return []
    can_learn = []
    for move in learnset:
        can_learn.append({'level': 'tm', 'moveId': move})

    return can_learn

def find_machine_no_by_waza_no(waza_no):
    for waza_machine in ItemTable['WazaMachine']:
        if waza_machine['wazaNo'] == waza_no:
            return waza_machine['machineNo']
    return None

def find_waza_no_by_machine_no(machineNo):
    for waza_machine in ItemTable['WazaMachine']:
        if waza_machine['machineNo'] == machineNo:
            return waza_machine['wazaNo']
    return None

def create_tm_learnset(move_ids):
    tm_bitfield = [0] * 256

    for move_id in move_ids:
        tm_no = find_machine_no_by_waza_no(move_id)
        if(tm_no == None):
            continue

        bit_index = tm_no - 1
        if bit_index > 256:
            continue

        tm_bitfield[bit_index] = 1
    return convert_to_32_bit_integers(tm_bitfield)

def create_move_id_learnset(binary_array):
    tm_array = []
    for machine_no_index, binary_int in enumerate(binary_array):
        if binary_int == 0:
            continue
        if machine_no_index > 103:
            break
        machine_no = machine_no_index + 1
        tm_array.append(find_waza_no_by_machine_no(machine_no))
    
    return tm_array

def get_pokemon_learnset(monsno=0):
    """
    This function can be surprisingly heavy, so I added a cache.
    Returns a list of moves per ID
    """
    learnset = learnset_data['WazaOboe'][monsno]['ar']
    move_list = []
    for i in range(0, len(learnset), 2):
        move_object = {}
        move_object['level'] = learnset[i]
        move_object['moveId'] = learnset[i + 1]
        move_list.append(move_object)

    pokemon_learnset = {}
    for e in move_list:
        level = e['level']
        move_id = e['moveId']
        if move_id not in _move_properties_cache:
            _move_properties_cache[move_id] = get_move_properties(move_id)
        name = _move_properties_cache[move_id]['name']
        pokemon_learnset[name] = level

    return pokemon_learnset

def get_level_learnset(pokemonId):
    learnset = learnset_data['WazaOboe'][pokemonId]['ar']
    move_list = []
    for i in range(0, len(learnset), 2):
        move_list.append(learnset[i + 1])
    return move_list

def get_moves(m1, m2, m3, m4, monsno, level, output_format):
    """
    If all the moves are zero, one should assume their learnset is generated by BDSP
    Otherwise, return moves are per their strings
    """
    if m1 == m2 and m1 == m3 and m1 == m4:
        return generate_moves_via_learnset(monsno, level, output_format)
    if output_format == constants.TRACKER_METHOD:
        return [m1, m2, m3, m4]

    moves = [
        move_enum[m1],
        move_enum[m2],
        move_enum[m3],
        move_enum[m4]
    ]

    if moves[0] is None:
        print(f"Moves: {m1}, {m2}, {m3}, {m4}, {monsno}, {moves}")
    
    return moves

def is_smogon_compatible(str):
    SMOGON_MOVES = full_data['smogon_moves']    
    for gen in SMOGON_MOVES:
        if str in gen.keys():
            return True
    return False

def get_move_string(move_id=0):
    moves_namedata = full_data['moves_namedata']
    name_data = moves_namedata['labelDataArray'][move_id]['wordDataArray']
    name = name_data[0]['str'] if name_data else 'None'
    if not is_smogon_compatible(name) and move_id != 0:
        raise ValueError(f'Incompatible move string found: ID - {move_id}, String: {name}')
    return name

def generate_moves_via_learnset(mons_no, level, output_format):
    """
    This function generates the learnset for a Pokemon by the inputted level.
    It does this by finding the 4 most recent moves in the list and returns them.
    """

    if not isinstance(mons_no, int) or mons_no < 0 or not learnset_data['WazaOboe'][mons_no]:
        raise ValueError('Invalid Pokémon number')

    if not isinstance(level, int) or level < 0:
        raise ValueError('Invalid level')

    moveset = learnset_data['WazaOboe'][mons_no]['ar']
    idx = next((i for i in range(0, len(moveset), 2) if moveset[i] > level), len(moveset))
    cutoff_index = next((i for i, current_move_or_level in enumerate(learnset_data['WazaOboe'][mons_no]['ar']) if i % 2 == 0 and current_move_or_level > level), len(learnset_data['WazaOboe'][mons_no]['ar']))
    moves = learnset_data['WazaOboe'][mons_no]['ar'][:cutoff_index]
    move_names = [get_move_string(move) for move in moves]
    if output_format == constants.TRACKER_METHOD:
        move_names = moves
    num_moves = len(moves)
    if num_moves >= 7:
        return [move_names[-7], move_names[-5], move_names[-3], move_names[-1]]
    elif num_moves >= 5:
        return [move_names[-5], move_names[-3], move_names[-1]]
    elif num_moves >= 3:
        return [move_names[-3], move_names[-1]]
    elif num_moves >= 1:
        return [move_names[-1]]
    else:
        return []

def get_move_id_from_move_name(move_name):
    moves_namedata = full_data['moves_namedata']

    if not move_name:
        return -1
    for i, move in enumerate(moves_namedata['labelDataArray']):
        if move['wordDataArray'][0]['str'] == move_name:
            return i
        if slugify(move['wordDataArray'][0]['str']) == move_name:
            return i
    return -1

def get_egg_moves(dex_id=0):
    """
    Requires the ID of a Pokemon, not the MonsNo, this is how we must handle Forms.
    """
    baby_pokemon_id = get_first_evo_pokemon_id(dex_id)
    egg_learnset = full_data['egg_learnset']['Data']

    egg_moves = egg_learnset[baby_pokemon_id]['wazaNo']
    return [{'level': 'egg', 'moveId': move_id} for move_id in egg_moves]

def get_egg_moves_list(pokemonId):
    '''Returns the list of move Ids that a pokemon can get through egg moves'''
    baby_pokemon_id = get_first_evo_pokemon_id(pokemonId)
    egg_learnset = full_data['egg_learnset']['Data']
    egg_moves = egg_learnset[baby_pokemon_id]['wazaNo']
    return egg_moves

def get_grass_knot_power(weightkg):
    """
    Allows you to display Grass Knot's Power on a certain Pokemon, because let's be real,
    no one really knows how much this move is going to do otherwise.
    """
    if weightkg >= 200:
        return 120
    elif weightkg >= 100:
        return 100
    elif weightkg >= 50:
        return 80
    elif weightkg >= 25:
        return 60
    elif weightkg >= 10:
        return 40
    else:
        return 20

def get_list_of_moves_by_type():
    '''
    This grabs all of the moves possible, grabs their id and outputs a text document
    It will be ordered by move type and then by move_id
    The output will be as follows:
    Pound|Normal
    Double Slap|Normal
    Comet Punch|Normal
    etc.
    '''
    moves = full_data['moves_table']['Waza']
    moves_list = defaultdict(list)
    with open(os.path.join(debug_file_path, "moves_by_types.txt"), "w") as output:
        for move in moves:
            move_props = get_move_properties(move['wazaNo'])
            move_type = move_props['type']
            move_name = move_props['name']
            moves_list[move_type].append(move_name)
        for move_type in moves_list.keys():
            for move_name in moves_list[move_type]:
                output.write(f"{move_name}|{move_type}\n")

def get_tutor_moves(monsno=0, formno=0):
    tutor_moves = full_data['tutor_moves']
    monsNo = str(monsno)
    formNo = str(formno)
    if monsno == 0:
        return []
    if monsNo not in tutor_moves.keys():
        return []
    if formNo not in tutor_moves[monsNo].keys():
        return []

    moveset = tutor_moves[monsNo][formNo]
    tutor_set = [{'moveLevel': 0, 'move': get_move_properties(move_id), 'moveId': move_id} for move_id in moveset]

    return tutor_set

def get_tutor_moves_list(monsno=0, formno=0):
    tutor_moves = full_data['tutor_moves']
    monsNo = str(monsno)
    formNo = str(formno)
    if monsno == 0:
        return []
    if monsNo not in tutor_moves.keys():
        return []
    if formNo not in tutor_moves[monsNo].keys():
        return []

    return tutor_moves[monsNo][formNo]

if __name__ != "__main__":
    full_data = load_data()
    learnset_data = full_data['learnset_data']
    ItemTable = full_data['item_table']

if __name__ == "__main__":
    full_data = load_data()
    get_list_of_moves_by_type()

