import json
import os
import re
import unicodedata

import constants
import poke_api_constants
from load_files import load_data
from moveUtils import (
    get_moves,
    get_pokemon_learnset,
    get_tech_machine_learnset,
    get_egg_moves,
    get_grass_knot_power,
    get_tutor_moves,
    get_move_string,
    get_level_learnset,
    get_tm_compatibility,
    get_egg_moves_list,
    get_tutor_moves_list,
    )
from pokemonTypes import get_type_name

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, constants.INPUT_NAME)
debug_file_path = os.path.join(parent_file_path, "Python_tasks", constants.DEBUG_NAME)
personal_data_path = os.path.join(input_file_path, 'PersonalTable.json')

FORM_MAP = {}
GENDER = {"0": "MALE", "1": "FEMALE", "2": "NEUTRAL"}

# Load all the JSON Data

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
    pokemonId = get_pokemon_id_from_mons_no_and_form(lumi_formula_mon, form_no)
    return pokemonId

def get_pokemon_name(pokemon_id = 0, form_mode = False):
    '''
    Trys 3 different ways of getting the pokemon name
    Replaces any trouble characters into workable characters
    '''
    form_namedata = full_data['form_namedata']
    try:
        pokemon_name = ""
        ## This first one checks if the pokemon_id is contained in the name_data
        if pokemon_id < len(name_data["labelDataArray"]):
            mons_name = name_data["labelDataArray"][pokemon_id]["wordDataArray"][0]["str"]
            form_name = form_namedata["labelDataArray"][pokemon_id]["wordDataArray"][0]["str"]

            if len(form_name) > 0 and mons_name not in form_name and form_mode == True:
                pokemon_name = f"{mons_name} {form_name}"
            elif len(form_name) > 0 and mons_name in form_name and form_mode == True:
                pokemon_name = form_name
            else:
                pokemon_name = mons_name
        elif pokemon_id > 2**16:
            pokemon_id = convert_lumi_formula_mon(pokemon_id)
            pokemon_name = get_form_name(pokemon_id)
        else:
            pokemon_name = get_form_name(pokemon_id)

        pokemon_name = pokemon_name.replace('♀', '-F')
        pokemon_name = pokemon_name.replace('♂', '-M')
        pokemon_name = pokemon_name.replace('’', '\u2019')
        return pokemon_name
    except Exception as e:
        print(pokemon_id, e)
        raise Exception(e)

def get_form_name(id):
    '''
    Checks if there are any 
    '''
    form_namedata = full_data['form_namedata']

    if id in constants.TROUBLE_MONS_NAMES.keys():
        return constants.TROUBLE_MONS_NAMES.get(id, None)
    else:
        form_data = form_namedata['labelDataArray'][id]
        form_name = form_data['wordDataArray'][0]['str']
        monsNo = form_data['labelName'].split("_")[-2]
        pokemon_name = get_pokemon_name(int(monsNo))
        if(pokemon_name not in form_name):
            return f"{pokemon_name} {form_name}"
        return form_name

def get_pokemon_id_from_mons_no_and_form(mons_no, form_no):
    for entry in personal_table["Personal"]:
        if (
            entry["monsno"] == mons_no
            and FORM_MAP[entry["monsno"]][form_no] == entry["id"]
        ):
            return entry["id"]
    return None  # Return None if no matching ID is found

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
    try:
        if not pokemon_name:
            return -1
        pokemonId = NAME_MAP[pokemon_name]
        return pokemonId
    except KeyError as e:
        raise Exception("This pokemon is not in the FORM_MAP:", e)
    except SyntaxError as e:
        print("This monsName is not formatted correctly to get a correct monsNo:", e)

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
        if slugify(item['wordDataArray'][0]['str']) == item_name:
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
    if monsno == 0:
        return 0

    height_string = pkmn_height_data['labelDataArray'][monsno]['wordDataArray'][0]['str'] or '0'
    if "'" in height_string:
        feet_string, inches_string = height_string.split("'")
    else:
        feet_string = '0'
        inches_string = height_string

    inches = float(inches_string[:-1] or '0')
    feet = int(feet_string)

    feet_in_centimeters = feet * 30.48
    inches_in_centimeters = inches * 2.54
    return round((feet_in_centimeters + inches_in_centimeters) / 100, 2)

def slugify(value, pokeapi=False):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores), converts spaces to hyphens, and rearranges string before
    the space at the end if the first part is "Mega" or "Gigantamax".
    Also strips leading and trailing whitespace.
    """
    initial_value = value
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    if pokeapi == False:
        return re.sub('[-\s]+', '-', value)

    if ' ' in value or "-" in value:
        # Split the string at the last space
        for bad_value in poke_api_constants.START_OF_LINE_FORMS.keys():
            if bad_value in value:
                value = value.replace(bad_value, poke_api_constants.START_OF_LINE_FORMS[bad_value])
        for bad_end_value in poke_api_constants.END_OF_LINE_FORMS.keys():
            if bad_end_value == value.split()[-1]:
                value = value.replace(f" {bad_end_value}", poke_api_constants.END_OF_LINE_FORMS[bad_end_value])
        parts = value.rsplit(' ', 1)
        
        # Check if the first part is "Mega" or "Gigantamax"
        if parts[0] in poke_api_constants.REVERSE_ORDER_ARRAY or parts[-1] == "genesect":
            # Rearrange string and join with hyphen
            value = '-'.join([parts[1], parts[0]])
            return value

    return re.sub('[-\s]+', '-', value)

def isSpecialPokemon(current_pokemon_name):
    """
    Returns true if the name of the Pokemon is Perrserker, Obstagoon, Indeedee, Meowstic or Sneasler.
    This is to retain intended behaviour the app depends on
    """
    return current_pokemon_name == "Indeedee" or current_pokemon_name == "Meowstic"

def create_diff_forms_dictionary(form_dict, mode = "2.0"):
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
        current_pokemon_name = get_pokemon_name(int(mons_no), mode != "2.0")

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

def get_pokemon_name_dictionary(mode = "2.0"):
    pokemon = {}
    for (idx, p) in enumerate(personal_data["Personal"]):
        monsNo = str(p["monsno"])
        if(idx == 0):
            continue
        if(not monsNo in pokemon):
            pokemon[monsNo] = []
        pokemon[monsNo].append(get_pokemon_name(p["id"], mode == "3.0"))
    return pokemon

def get_diff_form_dictionary(mode = "2.0"):
    return create_diff_forms_dictionary(get_pokemon_name_dictionary(mode), mode)

def get_pokemon_info(personalId=0):
    """
    BDSP works on an ID system, thus it is imperative to be able to swap between monsno and "ID", which is the index of the Pokemon in any of the relevant Pokemon gamefiles. 
    """
    tmLearnset = {}
    eggLearnset = {}
    tutorLearnset = {}

    p = personal_data['Personal'][int(personalId)]
    _, formNo = get_mons_no_and_form_no(personalId)
    tms = get_tech_machine_learnset(personalId)
    eggs = get_egg_moves(int(personalId))
    tutors = get_tutor_moves(p['monsno'], formNo)

    for tm in tms:
        tmLearnset[get_move_string(tm['moveId'])] = tm['moveId']

    for eggMoveDict in eggs:
        egg_move_id = eggMoveDict['moveId']
        eggLearnset[get_move_string(egg_move_id)] = egg_move_id

    for tutor in tutors:
        tutorLearnset[tutor["move"]["name"]] = tutor["moveId"]

    info_dict = {
        'id': p['id'],
        'monsno': p['monsno'],
        'formno': formNo,
        'name': get_pokemon_name(int(personalId)),
        'egg_group1': p['egg_group1'],
        'egg_group2': p['egg_group2'],
        'ability1': get_ability_string(p['tokusei1']),
        'ability2': get_ability_string(p['tokusei2']),
        'abilityH': get_ability_string(p['tokusei3']),
        'learnset': get_pokemon_learnset(int(personalId)),
        'tmLearnset': tmLearnset,
        'eggLearnset': eggLearnset,
        'tutorLearnset': tutorLearnset,
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
    with open(os.path.join(debug_file_path, "forms_format.json"), "w", encoding="utf-8") as output:
        json.dump(forms, output, ensure_ascii=False, indent=2)
    return forms

def get_mons_no_and_form_no(pokemon_id):
    if pokemon_id <= constants.POKEDEX_LENGTH:
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
        pokemonId = get_pokemon_id_from_mons_no_and_form(monsno, form)
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

def get_mon_full_learnset(pokemonId=0):
    '''
    Returns the full learnset and egg learnsets of a pokemon
    '''
    full_learnset = {
        "level": [],
        "tm": [],
        "egg": [],
        "tutor": [],
    }
    monsNo, formNo = get_mons_no_and_form_no(pokemonId)

    level_moves = get_level_learnset(pokemonId)
    if len(level_moves) > 0:
        full_learnset['level'] = level_moves

    tm_moves = get_tm_compatibility(pokemonId)
    if len(tm_moves) > 0:
        full_learnset['tm'] = tm_moves

    egg_moves = get_egg_moves_list(pokemonId)
    if (len(egg_moves)) > 0:
        full_learnset['egg'] = egg_moves

    tutor_moves = get_tutor_moves_list(monsNo, formNo)
    if len(tutor_moves) > 0:
        full_learnset['tutor'] = tutor_moves
    return full_learnset

if __name__ != '__main__':
    with open(personal_data_path, mode='r', encoding="utf-8") as f:
        personal_data = json.load(f)
        for curr in personal_data['Personal']:
            if curr['monsno'] not in FORM_MAP:
                FORM_MAP[curr['monsno']] = []
            FORM_MAP[curr['monsno']].append(curr['id'])

    full_data = load_data()
    personal_table = full_data['personal_table']
    name_data = full_data['raw_pokedex']
    forms = generate_form_name_to_pokemon_id()
    reversed_forms = {v: k for k, v in forms.items()}
    pokedex = get_lumi_data(name_data, get_pokemon_name)
    diff_forms, NAME_MAP = get_diff_form_dictionary(constants.GAME_MODE)

