import json
import os
import copy
import constants

from pokemonUtils import get_item_string, get_pokemon_name, get_pokemon_id_from_name

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, "input")
input_file_path3 = os.path.join(parent_file_path, "3.0Input")
output_file_path = os.path.join(parent_file_path, "Python_tasks", constants.OUTPUT_NAME)
debug_file_path = os.path.join(parent_file_path, "Python_tasks", constants.DEBUG_NAME)

personal_data_path = os.path.join(input_file_path, 'PersonalTable.json')
personal_data_path3 = os.path.join(input_file_path3, 'PersonalTable.json')

form_name_path = os.path.join(input_file_path, 'english_ss_zkn_form.json')
form_name_path3 = os.path.join(input_file_path3, 'english_ss_zkn_form.json')

new_to_old_personal_ids = {}
NEW_FORM_MAP = {}
OLD_FORM_MAP = {}

def create_new_to_old_p_ids():

  with open(personal_data_path3, mode="r", encoding="utf-8") as new_f, open(personal_data_path, mode="r", encoding="utf-8") as old_f:
    new_personal_data = json.load(new_f)
    old_personal_data = json.load(old_f)

    for curr in new_personal_data['Personal']:
      if curr['monsno'] not in NEW_FORM_MAP:
        NEW_FORM_MAP[curr['monsno']] = []
      NEW_FORM_MAP[curr['monsno']].append(curr['id'])

    for curr in old_personal_data['Personal']:
      if curr['monsno'] not in OLD_FORM_MAP:
        OLD_FORM_MAP[curr['monsno']] = []
      OLD_FORM_MAP[curr['monsno']].append(curr['id'])

    for pokemonId, personal_item in enumerate(new_personal_data["Personal"]):
      new_mons_no = personal_item["monsno"]
      new_form_no = NEW_FORM_MAP[new_mons_no].index(pokemonId)
      if new_mons_no in OLD_FORM_MAP:
        if (len(OLD_FORM_MAP[new_mons_no])) <= new_form_no:
          continue
        new_to_old_personal_ids[pokemonId] = OLD_FORM_MAP[new_mons_no][new_form_no]
      else:
        continue

  with open(form_name_path3, mode="r", encoding="utf-8") as new_name_f, open(form_name_path, mode="r+", encoding="utf-8") as old_name_f:
    new_name_data = json.load(new_name_f)
    old_name_data = json.load(old_name_f)
    copy_name_data = copy.deepcopy(old_name_data)

    for new_personal_id, old_personal_id in new_to_old_personal_ids.items():
      new_mons_name = new_name_data["labelDataArray"][new_personal_id]["wordDataArray"][0]["str"]
      old_mons_name = old_name_data["labelDataArray"][old_personal_id]["wordDataArray"][0]["str"]
      if not old_mons_name and new_mons_name != old_mons_name:
        old_mons_name = "NOTHING HERE ORIGINALLY"
      if new_mons_name != old_mons_name:
        print("Old Name:", old_mons_name, "New Name:", new_mons_name)
        copy_name_data["labelDataArray"][old_personal_id]["wordDataArray"][0]["str"] = new_mons_name

    with open(os.path.join(output_file_path, 'english_ss_zkn_form.json'), 'w') as output:
      output.write(json.dumps(copy_name_data, indent=2))

def write_new_names_to_item_images():
  directory = os.path.join(parent_file_path, "Python_tasks", "named_items")
  for filename in os.listdir(directory):
    if not filename.startswith("item"):
      continue
    if filename == "item_0000.png":
      continue

    item_number = filename.split("_")[1].split('.')[0].lstrip('0')
    item_name = get_item_string(int(item_number))

    split_item_name = item_name.replace("’", "").replace(" ", "_")

    new_filename = f"Item_{split_item_name}.png"

    old_filepath = os.path.join(directory, filename)
    new_filepath = os.path.join(directory, new_filename)

    if old_filepath != new_filepath:
      os.rename(old_filepath, new_filepath)

def get_all_encounters_and_evolutions():
  pokemon_list = []
  locations_path = os.path.join(debug_file_path, "pokemon_locations.json")
  statics_path = os.path.join(input_file_path, "static_area_locations.json")
  evolutions_path = os.path.join(input_file_path, "evolution.json")

  with open(locations_path, mode="r", encoding="utf-8") as pokemon_locations_file, \
      open(statics_path, mode="r", encoding="utf-8") as statics_locations_file, \
      open(evolutions_path, mode="r", encoding="utf-8") as evolutions_file:

    pokemon_locations = json.load(pokemon_locations_file)
    static_locations = json.load(statics_locations_file)
    evolutions = json.load(evolutions_file)

    for mons_no in pokemon_locations:
      for encounter in pokemon_locations[mons_no]:
        base_mon_name = encounter["pokemonName"]
        if base_mon_name not in pokemon_list:
          pokemon_list.append(base_mon_name)
        pokemon_id = get_pokemon_id_from_name(base_mon_name)
        mon_evolutions = evolutions[str(pokemon_id)]["path"]
        if base_mon_name.split()[0] == "Mothim":
          print(base_mon_name)
          print(mon_evolutions)
        for evo in mon_evolutions:
          evo_mon_name = get_pokemon_name(evo)
          if evo_mon_name not in pokemon_list:
            pokemon_list.append(evo_mon_name)
    for route in static_locations:
      for encounter in static_locations[route]:
        pokemon_name = encounter["pokemonName"]
        if pokemon_name not in pokemon_list:
          pokemon_list.append(pokemon_name)

        pokemon_id = get_pokemon_id_from_name(pokemon_name)
        static_evolutions = evolutions[str(pokemon_id)]["path"]
        for static_evo in static_evolutions:
          static_evo_name = get_pokemon_name(static_evo)
          if static_evo_name not in pokemon_list:
            pokemon_list.append(static_evo_name)


  # print(len(pokemon_list), pokemon_list)

if __name__ == "__main__":
  get_all_encounters_and_evolutions()