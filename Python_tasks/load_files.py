import csv
import json
import os
import re

from pokemonUtils import (create_diff_forms_dictionary, get_ability_string,
                          get_item_string, get_pokemon_name,
                          get_pokemon_name_dictionary)

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
resources_filepath = os.path.join(repo_file_path, "Python_tasks", "Resources")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")
POKEMON_NAMES = get_pokemon_name_dictionary()

def getTrainerIdsFromDocumentation():
    doc_filepath = os.path.join(input_file_path, "docs.csv")
    trainer_IDs = []
    with open(doc_filepath, "r")as doc_csv:
        csvreader = csv.reader(doc_csv)
        for row in csvreader:
            if row[0].isdigit():
                trainer_IDs.append(int(row[0]))
        return trainer_IDs

def get_lumi_data(raw_data, callback):
    data = {}
    for (idx, _) in enumerate(raw_data["labelDataArray"]):
        data[str(idx)] = callback(idx)
    return data

def load_json_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

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
        "rates": os.path.join(resources_filepath, 'Rates.json')
    }
    for name, filepath in files.items():
        data[name] = load_json_from_file(filepath)

    data["abilities"] = get_lumi_data(data["raw_abilities"], get_ability_string)
    data["pokedex"] = get_lumi_data(data["raw_pokedex"], get_pokemon_name)
    data["items"] = get_lumi_data(data["raw_items"], get_item_string)
    data["diff_forms"] = create_diff_forms_dictionary(POKEMON_NAMES)
    data["trainer_ids"] = getTrainerIdsFromDocumentation()

    return data
