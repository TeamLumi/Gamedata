import os
import json
import constants

from moveUtils import (
  get_tech_machine_learnset,
  create_tm_learnset,
  convert_int_to_bit,
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

    # These functions need to be worked on to get the right data.
    # LearnedList = get_tech_machine_learnset(pokemonID, True)
    # convertedInts = convert_int_to_bit(LearnedList)
    convertedInts = create_tm_learnset(LearnedList)

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

if __name__ == "__main__":
  # full_data = load_data()
  # personal_table = full_data["personal_table"]

  # This is only useful to grab from the poke_api_access output files.
  with open(os.path.join(debug_file_path, "New_Personal_Table.json"), "r") as json_file:
    personal_data = json.load(json_file)
  create_converted_tm_list()