import csv
import json
import os
import re

from json_cache import JsonCache

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
resources_filepath = os.path.join(repo_file_path, "Python_tasks", "Resources")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")

# Create an instance of JsonCache
json_cache = JsonCache()

def get_lumi_data(raw_data, callback):
    data = {}
    for (idx, _) in enumerate(raw_data["labelDataArray"]):
        data[str(idx)] = callback(idx)
    return data

def load_data():
    data = {}
    files = {
        "raw_encounters": os.path.join(input_file_path, "FieldEncountTable_d.json"),
        "raw_trainer_data": os.path.join(input_file_path, "TrainerTable.json"),
        "raw_abilities": os.path.join(input_file_path, "english_ss_tokusei.json"),
        "raw_pokedex": os.path.join(input_file_path, "english_ss_monsname.json"),
        "raw_items": os.path.join(input_file_path, "english_ss_itemname.json"),
        "routes": os.path.join(resources_filepath, "Routes.json"),
        "name_routes": os.path.join(resources_filepath, "NameRoutes.json"),
        "honey_routes": os.path.join(resources_filepath, "honeyroutes.json"),
        "trainer_names": os.path.join(input_file_path, 'english_dp_trainers_name.json'),
        "trainer_labels": os.path.join(input_file_path, 'english_dp_trainers_type.json'),
        "rates": os.path.join(resources_filepath, 'Rates.json'),
        "item_table": os.path.join(input_file_path, 'ItemTable.json'),
        "pkmn_height_data": os.path.join(input_file_path, 'english_ss_zkn_height.json'),
        "pkmn_weight_data": os.path.join(input_file_path, 'english_ss_zkn_weight.json'),
        "ability_namedata": os.path.join(input_file_path, 'english_ss_tokusei.json'),
        "type_namedata": os.path.join(input_file_path, 'english_ss_typename.json'),
        "form_namedata": os.path.join(input_file_path, 'english_ss_zkn_form.json'),
        'nature_namedata': os.path.join(input_file_path, 'english_ss_seikaku.json')
    }
    for name, filepath in files.items():
        data[name] = json_cache.get_json(filepath)  # Access the cached JSON data using json_cache

    return data
