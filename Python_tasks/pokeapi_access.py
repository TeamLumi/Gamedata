import pokebase
import json
import os
import sys
import copy
import csv

import constants
import poke_api_constants
from load_files import load_data
from pokemonUtils import get_pokemon_name, slugify, get_item_id_from_item_name, get_mons_no_and_form_no, get_form_pokemon_personal_id
from moveUtils import get_relumi_tm_compatibility, get_move_string, create_tm_learnset, get_tutor_moves_list
from pokemonTypes import get_type_id

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
input_file_path = os.path.join(repo_file_path, constants.INPUT_NAME)
stats_file_path = os.path.join(repo_file_path, "Python_tasks", "pokemon_stats")
debug_file_path = os.path.join(repo_file_path, "Python_tasks", constants.DEBUG_NAME)
tm_learnset_path = os.path.join(debug_file_path, "tm_learnsets")
official_tm_learnset_folder_path = os.path.join(os.path.join(repo_file_path, "TMLearnset"))
tutor_moves_list_path = os.path.join(debug_file_path, "MoveTutorLists")
vanilla_tutor_moves_path = os.path.join(debug_file_path, "move_tutor_learnsets")

def log_error(message):
  with open(os.path.join(debug_file_path, "error.txt"), "a", encoding="utf-8") as error_file:
    error_file.write(message + '\n')

def log_warning(message):
  with open(os.path.join(debug_file_path, "warning.txt"), "a", encoding="utf-8") as warning_file:
    warning_file.write(message + '\n')

def log_success(message):
  with open(os.path.join(debug_file_path, "success.txt"), "a", encoding="utf-8") as success_file:
    success_file.write(message + '\n')


def clear_logs():
  try:
    with open(os.path.join(debug_file_path, "error.txt"), "w", encoding="utf-8"):
      pass
    with open(os.path.join(debug_file_path, "warning.txt"), "w", encoding="utf-8"):
      pass
    with open(os.path.join(debug_file_path, "success.txt"), "w", encoding="utf-8"):
      pass
    print("Logs cleared successfully.")
  except Exception as e:
    print(f"Error: Unable to clear logs - {str(e)}")

def get_pokemon_learnsets():
  # Originally used for getting tm learnsets
  # tm_items = full_data["item_table"]
  # tm_moves = tm_items["WazaMachine"]
  all_moves = full_data["moves_table"]["Waza"]
  pokemon_tm_learnsets = {}
  print("Gathering TM Learnsets from PokeApi...")
  for index, move in enumerate(all_moves):
    # if index > 150:
    #   break
    move_no = move["wazaNo"]
    pokemon_list = None
    try:
      api_move = pokebase.move(move_no)
      pokemon_list = api_move.learned_by_pokemon
      # Enable this for Debug
      print(f"Move Pokemon List succesfully retrieved for {api_move.name}, Original: {get_move_string(move_no)}")
    except Exception as e:
      print(f"Error: {e}")

    try:
      for pokemon in pokemon_list:
        if pokemon.name not in pokemon_tm_learnsets.keys():
          pokemon_tm_learnsets[pokemon.name] = [move_no]
        else:
          pokemon_tm_learnsets[pokemon.name].append(move_no)
    except Exception as e:
      print(f"Error: {e}")
  file_name = "pokemon_all_moves_api_learnsets.json"
  with open(os.path.join(debug_file_path, file_name), "w", encoding="utf-8") as json_file:
    json.dump(pokemon_tm_learnsets, json_file, ensure_ascii=False, indent=2)
  print(f"Successfully wrote PokeApi Learnsets to {os.path.join(debug_file_path, file_name)}!")
  return pokemon_tm_learnsets

def get_pokeapi_mon_info(pokemon_name, pokemonId, monsno, counter):
  form = None
  pokemon = None
  species = None
  form_name = pokemon_name
  species_name = pokemon_name

  try:
    # Use pokebase to get Pokemon information
    if counter < 2:
      # counter is used for rerunning pokemon with their base forms
      form = pokebase.pokemon_form(pokemon_name)
      form_name = form.pokemon.name
    pokemon = pokebase.pokemon(form_name)
    if counter < 2:
      species_name = pokemon.species.name
    species = pokebase.pokemon_species(species_name)

  except AttributeError as e:
    if counter == 2:
      log_error(f"Error: Could not handle this pokemon: {pokemon_name} ({pokemonId})")
      return -1, -1, -1
    counter += 1
    if pokemon_name not in list(pokemon_all_move_learnsets.keys()):
      log_warning(f"Warning: {pokemon_name} ({pokemonId}) will be run again with their base form")
      new_mons_name = slugify(get_pokemon_name(monsno, pokemonId <= constants.POKEDEX_LENGTH), True)
      # get_pokemon_stats(new_mons_name, pokemonId, monsno, counter)
      get_tutor_move_assignments(new_mons_name, pokemonId, monsno, counter)
    return -1, -1, -1
  except Exception as e:
    log_error(f"Error: This pokemon is currently unavailable in PokeApi: {pokemon_name} ({pokemonId})")
    return -1, -1, -1

  return form, pokemon, species

def get_pokemon_stats(pokemon_name, pokemonId, monsno, counter=0):
  form, pokemon, species = get_pokeapi_mon_info(pokemon_name, pokemonId, monsno, counter)

  if form == -1:
    # An error has occurred in the get_pokeapi_mon_info
    return

  name_in_learnsets = 0
  if form:
    if form.name in list(pokemon_tm_learnsets.keys()):
      name_in_learnsets += 1
  if pokemon.name in list(pokemon_tm_learnsets.keys()):
    name_in_learnsets += 1
  if species:
    if species.name in list(pokemon_tm_learnsets.keys()):
      name_in_learnsets += 1
  if name_in_learnsets == 0:
    print(f"{pokemon_name} doesn't learn new moves")
    return

  try:
    monsNo, formNo = get_mons_no_and_form_no(pokemonId)
    original_tm_learnset = get_relumi_tm_compatibility(monsNo, formNo)    # Create a dictionary with Pokemon stats
    tm_learnset = pokemon_tm_learnsets.get(form.name if form else pokemon.name, None)
    if tm_learnset == None:
      tm_learnset = pokemon_tm_learnsets.get(species.name if species else pokemon.name)
    if tm_learnset == None and counter == 2:
      tm_learnset = []

    original_tm_learnset.extend(tm_learnset)
    reencoded_tm_learnset = create_tm_learnset(original_tm_learnset, 256)

    tm_learnset_names = []
    for tm in tm_learnset:
      tm_learnset_names.append(get_move_string(tm))

    pokemon_stats = {
      "name": form.name if form else pokemon.name,
      "id": pokemon.id,
      # "abilities": [int(ability.ability.url.split("/")[-2]) for ability in pokemon.abilities],
      # "types": [type_.type.name for type_ in (form.types if form else pokemon.types)],
      # "height": pokemon.height,
      # "weight": pokemon.weight,
      # "stats": {
      #   stat.stat.name: stat.base_stat
      #   for stat in pokemon.stats
      # },
      # "gender_ratio": poke_api_constants.GENDER_RATIOS[species.gender_rate],
      # "held_items": [
      #     {
      #         "held_item_no": get_item_id_from_item_name(item.item.name),
      #         "held_item_name": item.item.name,
      #         "rarity": item.version_details[-1].rarity
      #     }
      #     for item in pokemon.held_items
      #     if item.version_details[-1].rarity != 1
      # ],
      # "egg_groups": [
      #   poke_api_constants.EGG_GROUPS[egg_group.name]
      #   for egg_group in species.egg_groups
      # ],
      "tm_learnset": tm_learnset_names,
      "tm_bitfields": {
        "set01" : reencoded_tm_learnset[0],
        "set02" : reencoded_tm_learnset[1],
        "set03" : reencoded_tm_learnset[2],
        "set04" : reencoded_tm_learnset[3],
        "set05" : reencoded_tm_learnset[4],
        "set06" : reencoded_tm_learnset[5],
        "set07" : reencoded_tm_learnset[6],
        "set08" : reencoded_tm_learnset[7],
      }
    }

    # Write the dictionary to a JSON file
    file_name = f"monsno_{monsNo}_formno_{formNo}.json"
    with open(os.path.join(tm_learnset_path, file_name), "w", encoding="utf-8") as json_file:
      json.dump(pokemon_stats, json_file, ensure_ascii=False, indent=2)

    log_success(f"Stats for {form.name if form else pokemon.name} written to {file_name}")
  except TypeError as e:
    print(f"An error has occurred {e}")
    if counter == 2:
      log_error(f"Error: Could not find this pokemon in move lists: {pokemon_name} ({pokemonId})")
      return
    counter += 1
    log_warning(f"Warning: {pokemon_name} ({pokemonId}) does not have a tm learnset. Trying again with base form")
    new_mons_name = pokemon.species.name if pokemon else pokemon.name
    get_pokemon_stats(new_mons_name, pokemonId, monsno, counter)
  except AttributeError as e:
    log_error(f"Error: This pokemon is currently unavailable in PokeApi: {pokemon_name} ({pokemonId})")
    return

def write_pokeapi_data_to_file():
  print("Writing PokeApi data to file...")
  new_personal_table = copy.deepcopy(full_data["personal_table"])
  new_personal_data = new_personal_table["Personal"]
  for filename in os.listdir(stats_file_path):
    file_path = os.path.join(stats_file_path, filename)
    pokemonId = int(filename.split("_")[0])
    with open(file_path, "r", encoding="utf-8") as f:
      api_mon = json.load(f)
    new_pokemon_dict = new_personal_data[pokemonId]

    try:
      new_pokemon_dict["basic_hp"] = api_mon["stats"]["hp"]
      new_pokemon_dict["basic_atk"] = api_mon["stats"]["attack"]
      new_pokemon_dict["basic_def"] = api_mon["stats"]["defense"]
      new_pokemon_dict["basic_spatk"] = api_mon["stats"]["special-attack"]
      new_pokemon_dict["basic_spdef"] = api_mon["stats"]["special-defense"]
      new_pokemon_dict["basic_agi"] = api_mon["stats"]["speed"]

      new_pokemon_dict["type1"] = get_type_id(api_mon["types"][0])
      new_pokemon_dict["type2"] = get_type_id(api_mon["types"][0])
      if len(api_mon["types"]) > 1:
        new_pokemon_dict["type2"] = get_type_id(api_mon["types"][1])
      
      item_slots_conversion = {
        50: "item1",
        5: "item2",
        45: "item3",
      }
      new_pokemon_dict["item1"] = 0
      new_pokemon_dict["item2"] = 0
      new_pokemon_dict["item3"] = 0
      count_for_50s = 0
      for held_item in api_mon["held_items"]:
        if not held_item["rarity"]:
          continue
        if held_item["rarity"] == 100:
          new_pokemon_dict["item1"] = held_item["held_item_no"]
          new_pokemon_dict["item2"] = held_item["held_item_no"]
          new_pokemon_dict["item3"] = held_item["held_item_no"]
          break
        if held_item["rarity"] == 50:
          count_for_50s += 1
        if count_for_50s == 2:
          new_pokemon_dict["item2"] = held_item["held_item_no"]
          new_pokemon_dict["item3"] = held_item["held_item_no"]
          break
        rarity_conv = item_slots_conversion[held_item["rarity"]]
        new_pokemon_dict[rarity_conv] = held_item["held_item_no"]
      
      new_pokemon_dict["sex"] = api_mon["gender_ratio"]
      new_pokemon_dict["egg_group1"] = api_mon["egg_groups"][0]
      new_pokemon_dict["egg_group2"] = api_mon["egg_groups"][0]
      if len(api_mon["egg_groups"]) > 1:
        new_pokemon_dict["egg_group2"] = api_mon["egg_groups"][1]
      
      new_pokemon_dict["tokusei1"] = api_mon["abilities"][0]
      new_pokemon_dict["tokusei2"] = api_mon["abilities"][0]
      new_pokemon_dict["tokusei3"] = api_mon["abilities"][0]
      if len(api_mon["abilities"]) == 2:
        new_pokemon_dict["tokusei3"] = api_mon["abilities"][1]
      if len(api_mon["abilities"]) > 2:
        new_pokemon_dict["tokusei2"] = api_mon["abilities"][1]
        new_pokemon_dict["tokusei3"] = api_mon["abilities"][2]
      
      new_pokemon_dict["height"] = api_mon["height"] * 10
      new_pokemon_dict["weight"] = api_mon["weight"]

      for index, bitfield in enumerate(api_mon["tm_bitfields"]):
        new_pokemon_dict[f"machine{index + 1}"] = bitfield

    except Exception as e:
      print(f"Error: {e} {api_mon['name']} ({pokemonId})")

  with open(os.path.join(debug_file_path, "New_Personal_Table.json"), "w") as json_file:
    json.dump(new_personal_table, json_file, ensure_ascii=False, indent=4)
  print(f"Successfully wrote PokeApi data to {os.path.join(debug_file_path, 'New_Personal_Table.json')}")

def get_all_api_mon_data():
  print("Gathering all Pokemon data via PokeApi...")
  for pokemonId, mon in enumerate(personal_table):
    if mon["monsno"] < 284:
      continue
    if mon["monsno"] > 493:
      break
    mons_name = slugify(get_pokemon_name(pokemonId), True)
    get_pokemon_stats(mons_name, pokemonId, mon["monsno"])

def write_tm_101_to_150_learnsets():
  for file in os.listdir(tm_learnset_path):
    file_path = os.path.join(tm_learnset_path, file)
    with open(file_path, "r") as input:
      pokemon_learnset = json.load(input)["tm_bitfields"]

    official_tm_learnset_path = os.path.join(official_tm_learnset_folder_path, file)
    with open(official_tm_learnset_path, "w") as output:
      json.dump(pokemon_learnset, output, ensure_ascii=False, indent=2)

def get_tutor_move_assignments(pokemon_name, pokemonId, monsno, counter=0):
  monsNo, formNo = get_mons_no_and_form_no(pokemonId)
  file_name = f"monsno_{monsNo}_formno_{formNo}.json"
  if (os.path.exists(os.path.join(vanilla_tutor_moves_path, file_name))):
    # Don't start from the beginning every time
    return
  elif check_files_exist:
    print("This file doesn't exist yet:", file_name, "Pokemon name:", pokemon_name)
    return

  print(pokemon_name)
  form, pokemon, species = None, None, None
  if pokemon_name in list(poke_api_constants.API_NAME_KEY.keys()):
    print("Grabbing alternate name", pokemon_name)
    pokemon_name = poke_api_constants.API_NAME_KEY[pokemon_name]
  else:
    form, pokemon, species = get_pokeapi_mon_info(pokemon_name, pokemonId, monsno, counter)

  if (form == -1 or form == None) and pokemon_name not in list(pokemon_all_move_learnsets.keys()):
    # An error has occurred in the get_pokeapi_mon_info
    return

  name_in_learnsets = 0
  if form is not None and form != -1:
    if form.name in list(pokemon_all_move_learnsets.keys()):
      name_in_learnsets += 1
  if pokemon is not None and pokemon != -1:
    if pokemon.name in list(pokemon_all_move_learnsets.keys()):
      name_in_learnsets += 1
  if species is not None and species != -1:
    if species.name in list(pokemon_all_move_learnsets.keys()):
      name_in_learnsets += 1
  if pokemon_name in list(pokemon_all_move_learnsets.keys()):
    name_in_learnsets += 1
  if name_in_learnsets == 0:
    log_warning(f"{pokemon_name} doesn't learn moves")
    return

  try:
    final_tutor_moveset = []
    for moveId in move_tutor_lists:
      if moveId == 0:
        continue
      move_tutor_learnset = None
      if form != -1 and form != None:
        move_tutor_learnset = pokemon_all_move_learnsets.get(form.name if form else pokemon.name, None)
        if move_tutor_learnset == None:
          move_tutor_learnset = pokemon_all_move_learnsets.get(species.name if species else pokemon.name)
        if move_tutor_learnset == None and counter == 2:
          move_tutor_learnset = []
      if move_tutor_learnset == None:
        move_tutor_learnset = pokemon_all_move_learnsets.get(pokemon_name)

      lumi_tutor_move_learnset = get_tutor_moves_list(monsNo, formNo)

      if moveId in move_tutor_learnset or moveId in lumi_tutor_move_learnset:
        final_tutor_moveset.append(moveId)

    output_tutor_moveset = { "moves": final_tutor_moveset }
    with open(os.path.join(vanilla_tutor_moves_path, file_name), "w", encoding="utf-8") as json_file:
      json.dump(output_tutor_moveset, json_file, ensure_ascii=False, indent=2)

    if form != None and form != -1:
      log_success(f"Tutor Moves for {form.name if form else pokemon.name} written to {vanilla_tutor_moves_path}/{file_name}")
    else:
      log_success(f"Tutor Moves for {pokemon_name} written to {vanilla_tutor_moves_path}/{file_name}")
  except TypeError as e:
    print(f"An error has occurred {e}")
    if counter == 2:
      log_error(f"Error: Could not find this pokemon in move lists: {pokemon_name} ({pokemonId})")
      return
    counter += 1
    log_warning(f"Warning: {pokemon_name} ({pokemonId}) does not have a tutor learnset. Trying again with base form")
    new_mons_name = pokemon.species.name if pokemon else pokemon.name
    get_tutor_move_assignments(new_mons_name, pokemonId, monsno, counter)
  except AttributeError as e:
    print(e)
    log_error(f"Error: This pokemon is currently unavailable in PokeApi: {pokemon_name} ({pokemonId})")
    return

def get_all_tutor_move_data():
  print("Gathering all tutor move data via PokeApi...")
  for pokemonId, mon in enumerate(personal_table):
    if pokemonId == 0:
      continue
    if mon["monsno"] > 914 and mon["monsno"] not in poke_api_constants.EXCEPTION_IDS:
      continue
    if mon["monsno"] > 914:
      print(mon["monsno"])
    if pokemonId == 772:
      mons_name = "type-null"
    else:
      mons_name = slugify(get_pokemon_name(pokemonId), True)
    get_tutor_move_assignments(mons_name, pokemonId, mon["monsno"])

def output_tutor_moves_to_csv(output_csv_path="tutor_moves_output.csv"):
  with open(os.path.join(debug_file_path, output_csv_path), mode="w", newline='') as csv_file:
    writer = csv.writer(csv_file)

    move_tutor_names = []
    for moveId in move_tutor_lists:
      move_tutor_names.append(get_move_string(moveId))

    # Write header row
    header = ["mons_name", "monsNo", "formNo", "pokemonId"] + move_tutor_names
    writer.writerow(header)

    for filename in os.listdir(vanilla_tutor_moves_path):
      if not filename.endswith(".json"):
        continue

      file_parts = filename.replace(".json", "").split("_")
      if len(file_parts) < 4:
        continue  # skip invalid filenames

      try:
        monsNo = int(file_parts[1])
        formNo = int(file_parts[3])
      except ValueError:
        continue  # skip if conversion fails

      if monsNo > 914 and monsNo not in poke_api_constants.EXCEPTION_IDS:
        continue
      pokemonId = get_form_pokemon_personal_id(monsNo, formNo)
      mons_name = get_pokemon_name(pokemonId)

      with open(os.path.join(vanilla_tutor_moves_path, filename)) as mon_tutor_move_file:
        mon_tutor_moves = json.load(mon_tutor_move_file)

      mon_moves = mon_tutor_moves.get("moves", [])
      row = [mons_name, monsNo, formNo, pokemonId] + [moveId in mon_moves for moveId in move_tutor_lists]
      writer.writerow(row)


def full_run():
  # get_pokemon_learnsets()
  # clear_logs()
  # get_all_api_mon_data()
  # write_pokeapi_data_to_file()
  # write_tm_101_to_150_learnsets()
  # get_all_tutor_move_data()
  output_tutor_moves_to_csv()

if __name__ == "__main__":
  full_data = load_data()
  personal_table = full_data['personal_table']["Personal"]
  # with open(os.path.join(debug_file_path, "pokemon_api_learnsets.json"), "r") as json_file:
  #   pokemon_tm_learnsets = json.load(json_file)
  with open(os.path.join(debug_file_path, "pokemon_all_moves_api_learnsets.json"), "r") as move_file:
    pokemon_all_move_learnsets = json.load(move_file)

  check_files_exist = False # This is to print out a list of all the files that are still needed

  move_tutor_lists = []
  for filename in os.listdir(tutor_moves_list_path):
    if not filename.endswith(".meta"):
      with open(os.path.join(tutor_moves_list_path, filename)) as tutor_move_file:
        tutor_moves = json.load(tutor_move_file)
      move_tutor_lists.extend(tutor_moves["moves"])
  full_run()
