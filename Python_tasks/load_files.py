import csv
import json
import os
import re

from json_cache import JsonCache

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
resource_file_path = os.path.join(repo_file_path, "Python_tasks", "Resources")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")

# Create an instance of JsonCache
json_cache = JsonCache()

def custom_json_dump(obj, fp, *, indent=4):
    def format_json(obj, level):
        if isinstance(obj, list):
            if len(obj) == 0:
                return "[]"
            if all(isinstance(item, list) and len(item) == 2 for item in obj):
                result = "[\n"
                for item in obj:
                    result += f'{" " * (indent * (level + 1))}[{json.dumps(item[0])}, {json.dumps(item[1])}],\n'
                result = result[:-2] + "\n" + " " * (indent * level) + "]"
            else:
                result = "["
                for item in obj:
                    result += "\n" + " " * (indent * (level + 1)) + format_json(item, level + 1) + ","
                result = result[:-1] + "\n" + " " * (indent * level) + "]"
            return result
        elif isinstance(obj, dict):
            if len(obj) == 0:
                return "{}"
            result = "{"
            for key, value in obj.items():
                result += f'\n{" " * (indent * (level + 1))}"{key}": {format_json(value, level + 1)},'
            result = result[:-1] + "\n" + " " * (indent * level) + "}"
            return result
        else:
            return json.dumps(obj)

    formatted_json = format_json(obj, 0)
    fp.write(formatted_json)

def get_lumi_data(raw_data, callback):
    data = {}
    for (idx, _) in enumerate(raw_data["labelDataArray"]):
        data[str(idx)] = callback(idx)
    return data

def load_data():
    data = {}
    input_file_paths = {
        'ability_namedata': 'english_ss_tokusei.json',
        'area_display_names': 'english_dp_fld_areaname_display.json',
        'area_names': 'english_dp_fld_areaname.json',
        'egg_learnset': 'TamagoWazaTable.json',
        'form_namedata': 'english_ss_zkn_form.json',
        'item_table': 'ItemTable.json',
        'learnset_data': 'WazaOboeTable.json',
        'map_info': 'MapInfo.json',
        'move_info': 'english_ss_wazainfo.json',
        'moves_namedata': 'english_ss_wazaname.json',
        'moves_table': 'WazaTable.json',
        'nature_namedata': 'english_ss_seikaku.json',
        'pkmn_height_data': 'english_ss_zkn_height.json',
        'pkmn_weight_data': 'english_ss_zkn_weight.json',
        'raw_abilities': 'english_ss_tokusei.json',
        'raw_encounters': 'FieldEncountTable_d.json',
        'raw_items': 'english_ss_itemname.json',
        'raw_pokedex': 'english_ss_monsname.json',
        'raw_trainer_data': 'TrainerTable.json',
        'smogon_moves': 'moves.json',
        'trainer_labels': 'english_dp_trainers_type.json',
        'trainer_names': 'english_dp_trainers_name.json',
        'type_namedata': 'english_ss_typename.json',
        'personal_table': 'PersonalTable.json',
    }
    resource_file_paths = {
        'gym_leaders': 'NewGymLeaders.json',
        'honey_routes': 'honeyroutes.json',
        'rates': 'Rates.json',
        'routes': 'Routes.json',
        'special_trainer_names': 'SpecialTrainerNames.json',
        'name_routes': 'NameRoutes.json',
        'full_learnset': 'fullLearnset.json',
        'evolution_dex': 'evolution.json'
    }
    for name, filename in input_file_paths.items():
        file_path = os.path.join(input_file_path, filename)
        data[name] = json_cache.get_json(file_path)

    for name, filename in resource_file_paths.items():
        file_path = os.path.join(resource_file_path, filename)
        data[name] = json_cache.get_json(file_path)
   
    return data
