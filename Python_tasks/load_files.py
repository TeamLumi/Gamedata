import csv
import json
import os
import re

from json_cache import JsonCache
import constants
repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, constants.INPUT_NAME)
tm_file_path = os.path.join(repo_file_path, "TMLearnset")
resource_file_path = os.path.join(repo_file_path, "Python_tasks", "Resources")
output_file_path = os.path.join(repo_file_path, "Python_tasks", constants.OUTPUT_NAME)

# Create an instance of JsonCache
json_cache = JsonCache()

def get_lumi_data(raw_data, callback):
    data = {}
    for (idx, _) in enumerate(raw_data["labelDataArray"]):
        data[str(idx)] = callback(idx)
    return data

def load_data():
    data = {}
    input_file_paths = {
        # romfs/Data/StreamingAssets/AssetAssistant/Message/english
        'area_names': 'english_dp_fld_areaname.json',
        'area_display_names': 'english_dp_fld_areaname_display.json',
        'trainer_names': 'english_dp_trainers_name.json',
        'trainer_labels': 'english_dp_trainers_type.json',
        'raw_items': 'english_ss_itemname.json', # found in the common_msbt for 3.0
        'nature_namedata': 'english_ss_seikaku.json',
        'ability_namedata': 'english_ss_tokusei.json', # found in common_msbt for 3.0
        'type_namedata': 'english_ss_typename.json',
        'move_info': 'english_ss_wazainfo.json',
        'moves_namedata': 'english_ss_wazaname.json',


        # romfs/Data/StreamingAssets/AssetAssistant/Pml/personal_masterdatas
        'evolveTable': 'EvolveTable.json',
        'item_table': 'ItemTable.json',
        'personal_table': 'PersonalTable.json',
        'egg_learnset': 'TamagoWazaTable.json',
        'learnset_data': 'WazaOboeTable.json',
        'moves_table': 'WazaTable.json',


        # romfs/Data/StreamingAssets/AssetAssistant/Message/common_msbt
        'raw_pokedex': 'english_ss_monsname.json',
        'form_namedata': 'english_ss_zkn_form.json',
        'pkmn_height_data': 'english_ss_zkn_height.json',
        'pkmn_weight_data': 'english_ss_zkn_weight.json',


        # romfs/Data/StreamingAssets/AssetAssistant/Dpr/scriptableobjects/gamesettings
        'map_info': 'MapInfo.json',
        'raw_encounters': 'FieldEncountTable_d.json',


        # romfs/Data/StreamingAssets/AssetAssistant/Dpr/masterdatas
        'raw_trainer_data': 'TrainerTable.json',

        # These last ones are custom files
        'tutor_moves': 'tutorMoves.json',
        'smogon_moves': 'moves.json',
        'static_encounters': 'static_pokemon_locations.json',
        'evolution_dex': 'evolution.json',
    }
    resource_file_paths = {
        # Custom files created from various scripts
        'gym_leaders': 'NewGymLeaders.json',
        'honey_routes': 'honeyroutes.json',
        'rates': 'Rates.json',
        'routes': 'Routes.json',
        'special_trainer_names': 'SpecialTrainerNames.json',
        'name_routes': 'NameRoutes.json',
    }
    for name, filename in input_file_paths.items():
        file_path = os.path.join(input_file_path, filename)
        data[name] = json_cache.get_json(file_path)

    for name, filename in resource_file_paths.items():
        file_path = os.path.join(resource_file_path, filename)
        data[name] = json_cache.get_json(file_path)

    tms = {}
    for filename in os.listdir(tm_file_path):
        file_path = os.path.join(tm_file_path, filename)
        if filename.endswith(".meta"):
            continue

        tms[filename.split(".json")[0]] = json_cache.get_json(file_path)

    data["tm_learnsets"] = tms
    return data
