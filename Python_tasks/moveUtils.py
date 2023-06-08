import json
import os
import re
import unicodedata

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, 'input')
debug_file_path = os.path.join(parent_file_path, "Python_tasks", "Debug")
moves_namedata_file_path = os.path.join(input_file_path, 'english_ss_wazaname.json')
smogon_movedata_file_path = os.path.join(input_file_path, 'moves.json')
egg_learnset_file_path = os.path.join(input_file_path, 'TamagoWazaTable.json')
learnset_file_path = os.path.join(input_file_path, 'WazaOboeTable.json')
movestable_file_path = os.path.join(input_file_path, 'WazaTable.json')
move_info_file_path = os.path.join(input_file_path, 'english_ss_wazainfo.json')
item_table_file_path = os.path.join(input_file_path, 'ItemTable.json')
personal_data_path = os.path.join(input_file_path, 'PersonalTable.json')

move_enum = 0
SMOGON_MOVES = 0
learnset_data = 0
moves_namedata = 0
egg_learnset = 0
MovesTable = 0
move_info_data = 0
personal_data = 0
ItemTable = 0

FORM_MAP = {}
_move_properties_cache = {}  # cache for move properties

with open(personal_data_path, mode='r', encoding="utf-8") as f:
    personal_data = json.load(f)
    for curr in personal_data['Personal']:
        if curr['monsno'] not in FORM_MAP:
            FORM_MAP[curr['monsno']] = []
        FORM_MAP[curr['monsno']].append(curr['id'])

with open(item_table_file_path, mode='r', encoding="utf-8") as f:
    ItemTable = json.load(f)

with open(moves_namedata_file_path, mode='r', encoding="utf-8") as f:
    moves_namedata = json.load(f)

with open(movestable_file_path, mode='r', encoding="utf-8") as f:
    MovesTable = json.load(f)

with open(smogon_movedata_file_path, mode='r', encoding="utf-8") as f:
    SMOGON_MOVES = json.load(f)

with open(learnset_file_path, mode='r', encoding="utf-8") as f:
    learnset_data = json.load(f)

with open(os.path.join(input_file_path, 'moves.txt'), encoding="utf-8") as f:
    move_enum = [line.strip() for line in f if line.strip()]

with open(move_info_file_path, mode='r', encoding="utf-8") as f:
    move_info_data = json.load(f)

with open(egg_learnset_file_path, mode='r', encoding="utf-8") as f:
    egg_learnset = json.load(f)

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
    move = MovesTable['Waza'][move_id]
    type_ = move['type']
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
    word_data = move_info_data['labelDataArray'][move_id]['wordDataArray']
    description = ' '.join(wd['str'] for wd in word_data)
    return description

def parse_tm_learnset_section(dec):
    """
    TM learnset are stored in 4 separate 32 bit binary properties. This is the conversion function.
    """
    return bin(dec)[2:].zfill(32)[::-1]

def get_tech_machine_learnset(m1, m2, m3, m4):
    learnset = [parse_tm_learnset_section(m) for m in (m1, m2, m3, m4)]
    learnset = [int(bit) for bits in learnset for bit in bits]

    can_learn = []
    for i, has_move in enumerate(learnset):
        if not has_move:
            continue

        tm = ItemTable['WazaMachine'][i]
        can_learn.append({'level': 'tm', 'moveId': tm['wazaNo']})

    return can_learn

def get_pokemon_learnset(monsno=0):
    """
    This function can be surprisingly heavy, so I added a cache.
    Returns a list of moves per ID
    """
    learnset = learnset_data['WazaOboe'][monsno]['ar']
    move_list = [{'level': learnset[i], 'moveId': learnset[i + 1]} for i in range(0, len(learnset), 2)]

    pokemon_learnset = {}
    for e in move_list:
        level = e['level']
        move_id = e['moveId']
        if move_id not in _move_properties_cache:
            _move_properties_cache[move_id] = get_move_properties(move_id)
        name = _move_properties_cache[move_id]['name']
        pokemon_learnset[name] = level

    return pokemon_learnset

def get_moves(m1, m2, m3, m4, monsno, level, output_format):
    """
    If all the moves are zero, one should assume their learnset is generated by BDSP
    Otherwise, return moves are per their strings
    """
    if m1 == m2 and m1 == m3 and m1 == m4:
        return generate_moves_via_learnset(monsno, level, output_format)
    if output_format == "Tracker":
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
    for gen in SMOGON_MOVES:
        if str in gen.keys():
            return True
    return False

def get_move_string(id=0):
    str_ = move_enum[id]
    if not is_smogon_compatible(str_):
        raise ValueError(f'Incompatible move string found: ID - {id}, String: {str_}')
    return str_

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
    if output_format == "Tracker":
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

def get_move_id(move_name):
    if not move_name:
        return 0
    id = next((i for i, e in enumerate(move_enum) if e == move_name.strip()), -1)
    return id

def get_egg_moves(dex_id=0):
    """
    Requires the ID of a Pokemon, not the MonsNo, this is how we must handle Forms.
    """
    monsno = personal_data['Personal'][dex_id]['monsno']
    form_no = get_pokemon_form_id(monsno, dex_id)
    egg_moves = [e['wazaNo'] for e in egg_learnset['Data'] if e['no'] == monsno and e['formNo'] == form_no]
    return [{'level': 'egg', 'moveId': move_id} for move_id in egg_moves]

def get_grass_knot_power(weightkg):
    """
    Allows you to display Grass Knot's Power on a certain Pokemon, because let's be real, no one really knows how much this move is going to do otherwise.
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
