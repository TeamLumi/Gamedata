import os
import json
import constants

from moveUtils import (
  get_tech_machine_learnset,
  create_tm_learnset,
  convert_list_to_binary_array,
  create_move_id_learnset,
)
from pokemonUtils import get_mons_no_and_form_no, get_pokemon_name
from load_files import load_data

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, constants.INPUT_NAME)
debug_file_path = os.path.join(parent_file_path, "Python_tasks", constants.DEBUG_NAME)
stats_file_path = os.path.join(parent_file_path, "Python_tasks", "pokemon_stats")


def create_converted_tm_list():
  for pokemon in personal_data["Personal"]:
    if pokemon["id"] == 0:
      continue
    if pokemon["monsno"] <= 493:
      continue
    pokemonID = pokemon["id"]
    monsNo, formNo = get_mons_no_and_form_no(pokemonID)
    try:
      file_name = f"{pokemonID}_stats.json"
      with open(os.path.join(stats_file_path, file_name), "r", encoding="utf-8") as json_file:
        PokeApiData = json.load(json_file)
      LearnedList = PokeApiData["tm_learnset"]
    except:
      print(f"This pokemon's TMs are not available through PokeApi: {get_pokemon_name(pokemonID)} ({pokemonID})")
      continue

    tm_array_length = 256 if constants.GAME_MODE == constants.GAME_MODE_3 else 128
    convertedInts = create_tm_learnset(LearnedList, tm_array_length)

    outputObj = {
      "set01" : 0,
      "set02" : 0,
      "set03" : 0,
      "set04" : 0,
      "set05" : 0,
      "set06" : 0,
      "set07" : 0,
      "set08" : 0,
    }

    outputObj["set01"] = convertedInts[0]
    outputObj["set02"] = convertedInts[1]
    outputObj["set03"] = convertedInts[2]
    outputObj["set04"] = convertedInts[3]

    current_filepath = os.path.join(debug_file_path, "tm_conversion", f'monsno_{monsNo}_formno_{formNo}.json')
    with open( current_filepath, 'w') as file:
      json.dump(outputObj, file, ensure_ascii=False, indent = 2)

def swap_tms_to_move_ids_in_learnsets():
  for file in os.listdir(os.path.join(debug_file_path, "tm_conversion")):
    file_path = os.path.join(debug_file_path, "tm_conversion", file)
    with open(file_path, "r") as input:
      pokemon_learnset = json.load(input)

    tm_binary_list = convert_list_to_binary_array([
      pokemon_learnset["set01"],
      pokemon_learnset["set02"],
      pokemon_learnset["set03"],
      pokemon_learnset["set04"],
    ])
    tm_compatibility = create_move_id_learnset(tm_binary_list)

    tm_move_id_file_path = os.path.join(debug_file_path, "tm_move_id_learnsets", file)
    with open(tm_move_id_file_path, "w") as debug_output:
      json.dump(tm_compatibility, debug_output, ensure_ascii=False, indent=2)

def swap_move_ids_back_to_new_binary_learnsets():
  for file in os.listdir(os.path.join(debug_file_path, "tm_move_id_learnsets")):
    file_path = os.path.join(debug_file_path, "tm_move_id_learnsets", file)
    with open(file_path, "r") as input:
      pokemon_learnset = json.load(input)

    convertedInts = create_tm_learnset(pokemon_learnset, 256)

    outputObj = {
      "set01" : 0,
      "set02" : 0,
      "set03" : 0,
      "set04" : 0,
      "set05" : 0,
      "set06" : 0,
      "set07" : 0,
      "set08" : 0,
    }

    outputObj["set01"] = convertedInts[0]
    outputObj["set02"] = convertedInts[1]
    outputObj["set03"] = convertedInts[2]
    outputObj["set04"] = convertedInts[3]

    tm_binary_file_path = os.path.join(debug_file_path, "tm_conversion", file)
    with open(tm_binary_file_path, "w") as debug_output:
      json.dump(outputObj, debug_output, ensure_ascii=False, indent=2)

if __name__ == "__main__":
  # full_data = load_data()
  # personal_table = full_data["personal_table"]
  swap_move_ids_back_to_new_binary_learnsets()

  # This is only useful to grab from the poke_api_access output files.
  # with open(os.path.join(debug_file_path, "New_Personal_Table.json"), "r") as json_file:
  #   personal_data = json.load(json_file)
  # create_converted_tm_list()