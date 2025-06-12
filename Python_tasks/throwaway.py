import json
import os
import copy
import constants
import re
import UnityPy

from pokemonUtils import get_item_string, get_pokemon_name, get_pokemon_id_from_name

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

input_file_path = os.path.join(parent_file_path, "input")
input_file_path3 = os.path.join(parent_file_path, "3.0Input")
python_tasks_path = os.path.join(parent_file_path, "Python_tasks")

output_file_path = os.path.join(python_tasks_path, constants.OUTPUT_NAME)
debug_file_path = os.path.join(python_tasks_path, constants.DEBUG_NAME)
resources_file_path = os.path.join(python_tasks_path, "Resources")

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

def dummy_out_commands():
  scripts_directory = os.path.join(parent_file_path, "old_scripts")
  synonyms_file = os.path.join(resources_file_path, "command_synonyms.json")
  with open(synonyms_file, 'r', encoding="utf-8") as f:
    synonyms = json.load(f)

  new_synonyms = {}
  for synonym_key in synonyms:
    if not len(synonyms[synonym_key]) > 1:
      continue
    for command_name in synonyms[synonym_key]:
      new_synonyms[command_name] = synonyms[synonym_key][0]

  for filename in os.listdir(scripts_directory):
    file_path = os.path.join(scripts_directory, filename)
    new_file_path = os.path.join(parent_file_path, "new_scripts", filename)
    new_substrings = []
    with open(file_path, 'r', encoding="utf-8") as old_script:
      for line in old_script:
        command_name = re.match(r'^(?:\t| {1,4})(\w+)\(', line)
        if command_name is None:
          new_substrings.append(line)
        elif not command_name.group(1) in new_synonyms.keys():
          new_substrings.append(line)
        else:
          new_line = line.replace(command_name.group(1), new_synonyms[command_name.group(1)])
          new_substrings.append(new_line)
    with open(new_file_path, 'w', encoding="utf-8") as new_script:
      new_script.writelines(new_substrings)

def extract_and_print_bundle(bundle_path, filename):
    """
    Opens a Unity asset bundle and prints all MonoBehaviour objects inside it.
    :param bundle_path: Path to the Unity asset bundle file.
    """
    if not os.path.exists(bundle_path):
        print(f"Error: File '{bundle_path}' does not exist.")
        return

    # Load the Unity bundle
    env = UnityPy.load(bundle_path)
    extract_dir = os.path.join(python_tasks_path, "extracted_data")
    os.makedirs(extract_dir, exist_ok=True)

    # Iterate through all the objects in the bundle
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            try:
                # Export only the `_size` key
                if obj.serialized_type:
                    tree = obj.read_typetree()
                    if "_size" in tree:
                        print(f"{filename} has size: {tree['_size']}")
                        # unique_name = f"{filename}_size.json"
                        # fp = os.path.join(extract_dir, unique_name)
                        # with open(fp, "wt", encoding="utf8") as f:
                        #     json.dump({"_size": tree["_size"]}, f, ensure_ascii=False, indent=4)
                        # print(f"Exported '_size' key to: {fp}")
            except Exception as e:
                print(f"Error processing MonoBehaviour object: {e}")
                print("-" * 50)

def process_bundle_folder(folder_path):
    """
    Iterates through a folder of Unity bundles and prints their contents using extract_and_print_bundle.
    :param folder_path: Path to the folder containing Unity asset bundles.
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    for filename in os.listdir(folder_path):
        bundle_path = os.path.join(folder_path, filename)
        if os.path.isfile(bundle_path):
            extract_and_print_bundle(bundle_path, filename)

def compare_bundles(bundle_path1, bundle_path2, output_path):
    """
    Compares two Unity asset bundles and outputs the differences in MonoBehaviour objects into a JSON file.
    :param bundle_path1: Path to the first Unity asset bundle.
    :param bundle_path2: Path to the second Unity asset bundle.
    :param output_path: Path to the output JSON file for differences.
    """
    if not os.path.exists(bundle_path1) or not os.path.exists(bundle_path2):
        print("Error: One or both bundle files do not exist.")
        return

    # Load the Unity bundles
    env1 = UnityPy.load(bundle_path1)
    env2 = UnityPy.load(bundle_path2)

    differences = {}

    # Extract MonoBehaviour objects from both bundles
    def extract_mono_behaviours(env):
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour" and obj.serialized_type:
                tree = obj.read_typetree()
                if "_size" in tree:
                    return tree

    bundle1 = extract_mono_behaviours(env1)
    bundle2 = extract_mono_behaviours(env2)

    # Compare the MonoBehaviour objects
    all_keys = set(bundle1.keys()).union(set(bundle2.keys()))
    for key in all_keys:
        size1 = bundle1.get(key)
        size2 = bundle2.get(key)
        if size1 == size2:
            differences[key] = {f"yisuno_bundle_{key}": size1, f"vanilla_bundle_{key}": size2}

    # Write differences to a JSON file
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(differences, f, ensure_ascii=False, indent=4)

    print(f"Differences written to {output_path}")

def compare_folders(folder_path1, folder_path2, output_folder):
    """
    Compares all files across two folders and outputs the differences into JSON files.
    Each JSON file is named after the original file with "_differences.json" appended.
    :param folder_path1: Path to the first folder.
    :param folder_path2: Path to the second folder.
    :param output_folder: Path to the folder where difference JSON files will be saved.
    """
    if not os.path.exists(folder_path1) or not os.path.exists(folder_path2):
        print("Error: One or both folders do not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)

    # Get the list of files in both folders
    files1 = set(os.listdir(folder_path1))
    files2 = set(os.listdir(folder_path2))

    # Find common files
    common_files = files1.intersection(files2)

    for filename in common_files:
        file_path1 = os.path.join(folder_path1, filename)
        file_path2 = os.path.join(folder_path2, filename)

        output_file = os.path.join(output_folder, f"{filename}_differences.json")

        compare_bundles(file_path1, file_path2, output_file)


if __name__ == "__main__":
    # dummy_out_commands()
    # Replace this with the path to your Unity asset bundle
    # bundle_path = os.path.join(python_tasks_path, 'battle_bundles', 'pm0003_00_00')
    # print("hello world")
    # extract_and_print_bundle(bundle_path)

    # Replace this with the path to your folder of Unity asset bundles
    folder_path = os.path.join(resources_file_path, 'battle_bundles')
    print("This is now starting")
    # process_bundle_folder(folder_path)

    # Example usage
    # bundle_path1 = os.path.join(resources_file_path, 'battle_bundles', 'bundle1')
    # bundle_path2 = os.path.join(resources_file_path, 'vanilla_battle_bundles', 'bundle2')
    # output_path = os.path.join(debug_file_path, 'bundle_differences.json')

    # compare_bundles(bundle_path1, bundle_path2, output_path)

    # Example usage for folder comparison
    folder_path1 = os.path.join(resources_file_path, 'battle_bundles')
    folder_path2 = os.path.join(resources_file_path, 'vanilla_battle_bundles')
    output_folder = os.path.join(debug_file_path, 'folder_differences')

    compare_folders(folder_path1, folder_path2, output_folder)
