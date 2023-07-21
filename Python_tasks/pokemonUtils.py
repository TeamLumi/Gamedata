import json
import os
import re
import unicodedata

import constants
from load_files import load_data
from moveUtils import (get_moves, get_pokemon_learnset, get_tech_machine_learnset, get_egg_moves, get_grass_knot_power)
from pokemonTypes import get_type_name

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, 'input')
debug_file_path = os.path.join(parent_file_path, "Python_tasks", "Debug")
personal_data_path = os.path.join(input_file_path, 'PersonalTable.json')

personal_data = 0
FORM_MAP = {}
GENDER = {"0": "MALE", "1": "FEMALE", "2": "NEUTRAL"}

# Load all the JSON Data

with open(personal_data_path, mode='r', encoding="utf-8") as f:
    personal_data = json.load(f)
    for curr in personal_data['Personal']:
        if curr['monsno'] not in FORM_MAP:
            FORM_MAP[curr['monsno']] = []
        FORM_MAP[curr['monsno']].append(curr['id'])

def get_lumi_data(raw_data, callback):
    data = {}
    for (idx, _) in enumerate(raw_data["labelDataArray"]):
        data[str(idx)] = callback(idx)
    return data

def make_ability_object(ha):
    ability_namedata = full_data['ability_namedata']

    abilityString = ability_namedata["labelDataArray"][ha]["wordDataArray"][0]["str"]
    return {0: abilityString}

def convert_lumi_formula_mon(lumi_mons_no):
    # converts anything more than 2^16 (65,536) to it's correct PID
    form_no = lumi_mons_no//(2**16)
    lumi_formula_mon = lumi_mons_no - (form_no * (2**16))
    pkmn_key = pokedex[str(lumi_formula_mon)] + str(form_no)
    mons_no = diff_forms[pkmn_key][0]
    return mons_no

def get_pokemon_name(mons_no = 0):
    '''
    Trys 3 different ways of getting the pokemon name
    Replaces any trouble characters into workable characters
    '''
    try:
        pokemon_name = ""
        if mons_no < len(name_data["labelDataArray"]):
            pokemon_name = name_data["labelDataArray"][mons_no]["wordDataArray"][0]["str"]
        elif mons_no > 2**16:
            pokemon_id = convert_lumi_formula_mon(mons_no)
            pokemon_name = get_form_name(pokemon_id)
        else:
            pokemon_name = get_form_name(mons_no)

        pokemon_name = pokemon_name.replace('♀', '-F')
        pokemon_name = pokemon_name.replace('♂', '-M')
        pokemon_name = pokemon_name.replace('’', '\u2019')
        return pokemon_name
    except Exception as e:
        print(mons_no, e)

def get_form_name(id):
    '''
    Checks if there are any 
    '''
    form_namedata = full_data['form_namedata']
    new_trouble_pokemon_names = { 
        # This is to test the 3.0 data
        1245: 'Ash-Greninja',
        1288: 'Meowstic-F',
        1314: 'Rockruff Own-Tempo',
        1445: 'Indeedee-F',
        1459: 'Basculegion-F',
        1461: 'Oinkologne-F',
        1067: "Galarian Farfetch'd"
    }
    trouble_pokemon_names = {
        1242: 'Ash-Greninja',
        1285: 'Meowstic-F',
        1310: 'Rockruff Own-Tempo',
        1441: 'Indeedee-F',
        1454: 'Basculegion-F',
        1456: 'Oinkologne-F',
        1067: "Galarian Farfetch'd"
    }
    if id in trouble_pokemon_names.keys():
        return trouble_pokemon_names.get(id, None)
    else:
        name = form_namedata['labelDataArray'][id]['wordDataArray'][0]['str']
        dexNum = form_namedata['labelDataArray'][id]['labelName'].split("_")[-2]
        if(name == ""):
            return get_pokemon_name(id)
        if(get_pokemon_name(int(dexNum)) not in name):
            return get_pokemon_name(int(dexNum)) + ' ' + name
        return name

def get_item_string(item_id):
    item_namedata = full_data['raw_items']

    item_data = item_namedata["labelDataArray"][item_id]["wordDataArray"]
    if(len(item_data) == 0):
        return 'None'
    return item_data[0]["str"]

def get_ability_string(ability_id):
    ability_namedata = full_data['ability_namedata']

    ability_string = ability_namedata["labelDataArray"][ability_id]["wordDataArray"][0]["str"]
    if not ability_string:
        print(f"Missing ability string for ID {ability_id}")
    return ability_string

def get_nature_name(natureId):
    nature_namedata = full_data['nature_namedata']

    return nature_namedata["labelDataArray"][natureId]["wordDataArray"][0]["str"]

def get_ability_id_from_ability_name(ability_string):
    if not ability_string:
        return -1
    ability_id = next((i for i, e in enumerate(ability_namedata['labelDataArray']) if e['wordDataArray'][0]['str'] == ability_string), -1)
    return ability_id

def get_pokemon_id_from_name(pokemon_name):
    if not pokemon_name:
        return -1
    return NAME_MAP[pokemon_name]

def get_nature_id(nature_string):
    nature_namedata = full_data['nature_namedata']
    if not nature_string:
        return -1
    nature_id = next((i for i, e in enumerate(nature_namedata['labelDataArray']) if e['wordDataArray'][0]['str'] == nature_string), -1)
    return nature_id

def get_item_id_from_item_name(item_name):
    item_namedata = full_data['raw_items']

    if not item_name:
        return -1
    for i, item in enumerate(item_namedata['labelDataArray']):
        if item['wordDataArray'][0]['str'] == item_name:
            return i
    return -1

def get_gender(sex):
    if sex == 0:
        return 'M'
    elif sex == 254:
        return 'F'
    elif sex == 255:
        return 'N'
    return None

def get_pokemon_form_id(monsno=0, id_=0):
    """
    BDSP does not view Pokemon in a format such as "MonsNo 3, Form 2".
    In order to get such a list for easier reasoning, one must generate it.
    That is what FORM_MAP does, and we should use it across all the util functions. 

    MonsNo (int): [form0 (Vanilla, ie. Bulbasaur), form1, ...]
    """
    return FORM_MAP[monsno].index(id_)

def get_form_pokemon_personal_id(monsno=0, formNo=0):
    try:
        return FORM_MAP[int(monsno)][int(formNo)]
    except IndexError:
        return None

def get_weight(monsno=0):
    """
    Returns the weight per the metric system
    """
    pkmn_weight_data = full_data['pkmn_weight_data']

    monsno = int(monsno)
    if monsno != 0:
        weightString = pkmn_weight_data['labelDataArray'][monsno]['wordDataArray'][0]['str'] if (pkmn_weight_data['labelDataArray'][monsno]['wordDataArray'][0] is not None) else '0'
        weightString = weightString.replace(u'\xa0', u' ')
        poundsString = weightString.split(u" ")[0]
        poundsString = poundsString.strip()
        pounds = float(poundsString)

        poundsInKilogram = pounds * 0.453592
        return round(poundsInKilogram, 2)
    else:
        return 0

def get_height(monsno=0):
    """
    Returns the Pokemon's height per the metric sytem.
    """
    pkmn_height_data = full_data['pkmn_height_data']

    monsno = int(monsno)
    if monsno != 0:
        height_string = pkmn_height_data['labelDataArray'][monsno]['wordDataArray'][0]['str'] or '0'
        feet_string, inches_string = height_string.split("'")
        inches = float(inches_string[:-1])
        feet = int(feet_string)

        feet_in_centimeters = feet * 30.48
        inches_in_centimeters = inches * 2.54
        return round((feet_in_centimeters + inches_in_centimeters) / 100, 2)
    else:
        return 0

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)

def isSpecialPokemon(current_pokemon_name):
    """
    Returns true if the name of the Pokemon is Perrserker, Obstagoon, Indeedee, Meowstic or Sneasler.
    This is to retain intended behaviour the app depends on
    """
    return current_pokemon_name == "Indeedee" or current_pokemon_name == "Meowstic"

def create_diff_forms_dictionary(form_dict):
    """
    Each monsno will have an array of all the Pokemon names and forms.
    Add the current index to the name of the first object in the list as the key
    Find out why the number is what it is
    Add the current value as the second value in the array
    Add the slugged current value as the third value in the array
    """
    diff_forms = {}
    NAME_MAP = {}    
    for mons_no in form_dict.keys():
        mons_array = form_dict[mons_no]
        current_pokemon_name = get_pokemon_name(int(mons_no))

        for (idx, mon) in enumerate(mons_array):
            if idx != 0 or isSpecialPokemon(current_pokemon_name):
                mon_zeros = 3 - len(str(mons_no))
                form_zeros = 3 - len(str(idx))
                form_format = f"ZKN_FORM_{mon_zeros*'0'}{mons_no}_{form_zeros*'0'}{idx}"
                if form_format in forms.keys():
                    pokemon_id = forms[form_format]
                if isSpecialPokemon(current_pokemon_name):
                    pokemon_id = int(mons_no)
                
                diff_forms[current_pokemon_name + (str(idx or 1)) ] = [pokemon_id, mon, slugify(mon), mons_no, idx or 1]
                NAME_MAP[mon] = pokemon_id
            else:
                NAME_MAP[mon] = int(mons_no)
    with open(os.path.join(debug_file_path, "diff_forms_output.json"), "w", encoding="utf-8") as output:
        json.dump(diff_forms, output, ensure_ascii=False, indent=2)
    return diff_forms, NAME_MAP

def get_pokemon_name_dictionary():
    pokemon = {}
    for (idx, p) in enumerate(personal_data["Personal"]):
        if(idx == 0):
            continue
        if(not str(p["monsno"]) in pokemon):
            pokemon[str(p["monsno"])] = []
        pokemon[str(p["monsno"])].append(get_pokemon_name(p["id"]))
    return pokemon

def get_diff_form_dictionary():
    return create_diff_forms_dictionary(get_pokemon_name_dictionary())

def get_pokemon_info(personalId=0):
    """
    BDSP works on an ID system, thus it is imperative to be able to swap between monsno and "ID", which is the index of the Pokemon in any of the relevant Pokemon gamefiles. 
    """
    p = personal_data['Personal'][int(personalId)]

    info_dict = {
        'id': p['id'],
        'monsno': p['monsno'],
        'name': get_pokemon_name(int(personalId)),
        'ability1': get_ability_string(p['tokusei1']),
        'ability2': get_ability_string(p['tokusei2']),
        'abilityH': get_ability_string(p['tokusei3']),
        'learnset': get_pokemon_learnset(int(personalId)),
        'tmLearnset': get_tech_machine_learnset(p['machine1'], p['machine2'], p['machine3'], p['machine4']),
        'eggLearnset': get_egg_moves(int(personalId)),
        'baseStats': {
            'hp': p['basic_hp'], 'atk': p['basic_atk'], 'def': p['basic_def'], 
            'spa': p['basic_spatk'], 'spd': p['basic_spdef'], 'spe': p['basic_agi']
        },
        'baseStatsTotal': p['basic_hp'] + p['basic_atk'] + p['basic_def'] + p['basic_spatk'] + p['basic_spdef'] + p['basic_agi'],
        'weight': get_weight(personalId),
        'height': get_height(personalId),
        'grassKnotPower': get_grass_knot_power(get_weight(personalId)),
        'type': get_type_name(p['type1']),
    }

    if p['type2'] != p['type1']:
        info_dict['dualtype'] = get_type_name(p['type2'])
    else:
        info_dict['dualtype'] = 0
    info_dict['held_item1'] = get_item_string(p['item1'])
    info_dict['held_item2'] = get_item_string(p['item2'])
    info_dict['held_item3'] = get_item_string(p['item3'])
    return info_dict

def generate_form_name_to_pokemon_id():
    form_namedata = full_data['form_namedata']
    forms_list = form_namedata["labelDataArray"]
    forms = {}
    for all_forms in forms_list:
        formNo = int(all_forms["labelName"].split("_")[-1])
        if all_forms["arrayIndex"] != 0 and formNo > 000:
            forms[all_forms["labelName"]] = all_forms["arrayIndex"]
    return forms

def get_mons_no_and_form_no(pokemon_id):
    if pokemon_id < 1010:
        return pokemon_id, 0
    form_format = reversed_forms[pokemon_id].split("_")
    mons_no = int(form_format[-2].lstrip("0"))
    form_no = int(form_format[-1].lstrip("0"))
    return mons_no, form_no

def get_pokemon_from_trainer_info(trainer, output_format):
    pokemon_list = []
    for poke_num in range(1,7):
        level = trainer[f"P{poke_num}Level"]
        if level <= 0:
            break
        ability = get_ability_string(trainer[f"P{poke_num}Tokusei"])
        gender = constants.GENDER[str(trainer[f"P{poke_num}Sex"])] if trainer[f"P{poke_num}Sex"] != 3 else constants.GENDER["1"] #Female
        monsno = trainer[f"P{poke_num}MonsNo"]

        moves = [trainer[f"P{poke_num}Waza{j+1}"] for j in range(4)]
        m1, m2, m3, m4 = moves[0], moves[1], moves[2], moves[3]
        moves = get_moves(m1, m2, m3, m4, monsno, level, output_format)

        form = trainer[f"P{poke_num}FormNo"]
        pokemonId = diff_forms[pokedex[str(trainer[f"P{poke_num}MonsNo"])] + str(form)][0] if form > 0 and output_format == constants.TRACKER_METHOD else monsno
        trainer_item = trainer[f"P{poke_num}Item"]
        item = get_item_string(trainer_item) if trainer_item != 0 else None
        pokemon = {
            "ability": ability,
            "gender": gender,
            "id": pokemonId,
            "item": item,
            "level": level,
            "moves": moves,
            "nature": get_nature_name(trainer[f"P{poke_num}Seikaku"]),
            "ivatk": trainer[f"P{poke_num}TalentAtk"],
            "ivdef": trainer[f"P{poke_num}TalentDef"],
            "ivhp": trainer[f"P{poke_num}TalentHp"],
            "ivspatk": trainer[f"P{poke_num}TalentSpAtk"],
            "ivspdef": trainer[f"P{poke_num}TalentSpDef"],
            "ivspeed": trainer[f"P{poke_num}TalentAgi"],
            "evhp": trainer[f"P{poke_num}EffortHp"],
            "evatk": trainer[f"P{poke_num}EffortAtk"],
            "evdef": trainer[f"P{poke_num}EffortDef"],
            "evspatk": trainer[f"P{poke_num}EffortSpAtk"],
            "evspdef": trainer[f"P{poke_num}EffortSpDef"],
            "evspeed": trainer[f"P{poke_num}EffortAgi"]
        }
        pokemon_list.append(pokemon)
    return pokemon_list

if __name__ != '__main__':
    full_data = load_data()
    forms = generate_form_name_to_pokemon_id()
    reversed_forms = {v: k for k, v in forms.items()}
    name_data = full_data['raw_pokedex']
    pokedex = get_lumi_data(name_data, get_pokemon_name)
    diff_forms, NAME_MAP = get_diff_form_dictionary()

