import pokebase
import json
import os
import sys

import constants
import poke_api_constants
from load_files import load_data
from pokemonUtils import get_pokemon_name, slugify
from moveUtils import create_tm_learnset

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
input_file_path = os.path.join(repo_file_path, constants.INPUT_NAME)
stats_file_path = os.path.join(repo_file_path, "Python_tasks", "pokemon_stats")
debug_file_path = os.path.join(repo_file_path, "Python_tasks", constants.DEBUG_NAME)

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

def get_pokemon_tm_learnsets():
  tm_items = full_data["item_table"]
  tm_moves = tm_items["WazaMachine"]
  pokemon_tm_learnsets = {}
  for tm in tm_moves:
    tm_move_no = tm["wazaNo"]
    pokemon_list = None
    try:
      api_move = pokebase.move(tm_move_no)
      pokemon_list = api_move.learned_by_pokemon
      print(f"Move Pokemon List succesfully retrieved for {api_move.name}")
    except Exception as e:
      print(f"Error: {e}")

    try:
      for pokemon in pokemon_list:
        if pokemon.name not in pokemon_tm_learnsets.keys():
          pokemon_tm_learnsets[pokemon.name] = [tm_move_no]
        else:
          pokemon_tm_learnsets[pokemon.name].append(tm_move_no)
    except Exception as e:
      print(f"Error: {e}")
  with open(os.path.join(debug_file_path, "pokemon_api_learnsets.json"), "w", encoding="utf-8") as json_file:
    json.dump(pokemon_tm_learnsets, json_file, ensure_ascii=False, indent=2)
  return pokemon_tm_learnsets

def get_pokemon_stats(pokemon_name, pokemonId, monsno, counter=0):
  form = None
  pokemon = None
  species = None
  form_name = pokemon_name
  species_name = pokemon_name
  with open(os.path.join(debug_file_path, "pokemon_api_learnsets.json"), "r") as json_file:
    pokemon_tm_learnsets = json.load(json_file)
  try:
    # Use pokebase to get Pokemon information
    if counter < 2:
      form = pokebase.pokemon_form(pokemon_name)
      form_name = form.pokemon.name
    pokemon = pokebase.pokemon(form_name)
    if counter < 2:
      species_name = pokemon.species.name
    species = pokebase.pokemon_species(species_name)

  except AttributeError as e:
    if counter == 2:
      log_error(f"Error: Could not handle this pokemon: {pokemon_name} ({pokemonId})")
      return
    counter += 1
    log_warning(f"Warning: {pokemon_name} ({pokemonId}) will be run again with their base form")
    new_mons_name = slugify(get_pokemon_name(monsno, pokemonId <= constants.POKEDEX_LENGTH), True)
    get_pokemon_stats(new_mons_name, pokemonId, monsno, counter)
    return
  except Exception as e:
    log_error(f"Error: This pokemon is currently unavailable in PokeApi: {pokemon_name} ({pokemonId})")
    return

  try:
    # Create a dictionary with Pokemon stats
    tm_learnset = pokemon_tm_learnsets.get(form.name if form else pokemon.name, None)
    if tm_learnset == None:
      tm_learnset = pokemon_tm_learnsets.get(species.name if species else pokemon.name)
    if tm_learnset == None and counter == 2:
      tm_learnset = []

    pokemon_stats = {
      "name": form.name if form else pokemon.name,
      "id": pokemon.id,
      "abilities": [int(ability.ability.url.split("/")[-2]) for ability in pokemon.abilities],
      "types": [type_.type.name for type_ in (form.types if form else pokemon.types)],
      "height": pokemon.height,
      "weight": pokemon.weight,
      "stats": {
        stat.stat.name: stat.base_stat
        for stat in pokemon.stats
      },
      "gender_ratio": poke_api_constants.GENDER_RATIOS[species.gender_rate],
      "held_items": [
        {
          "held_item_no": int(item.item.url.split("/")[-2]),
          "held_item_name": item.item.name,
          "rarity": item.version_details[-1].rarity
        }
        for item in pokemon.held_items
      ],
      "egg_groups": [
        poke_api_constants.EGG_GROUPS[egg_group.name]
        for egg_group in species.egg_groups
      ],
      "tm_learnset": tm_learnset,
      "tm_bitfields": create_tm_learnset(tm_learnset)
    }

    # Write the dictionary to a JSON file
    file_name = f"{pokemonId}_stats.json"
    with open(os.path.join(stats_file_path, file_name), "w", encoding="utf-8") as json_file:
      json.dump(pokemon_stats, json_file, ensure_ascii=False, indent=2)

    log_success(f"Stats for {form.name if form else pokemon.name} written to {file_name}")
  except TypeError as e:
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

if __name__ == "__main__":
  full_data = load_data()
  personal_table = full_data['personal_table']["Personal"]
  clear_logs()
  for pokemonId, mon in enumerate(personal_table):
    # if pokemonId <= constants.POKEDEX_LENGTH:
    #   continue
    if mon["monsno"] <= 493:
      continue
    mons_name = slugify(get_pokemon_name(pokemonId), True)
    get_pokemon_stats(mons_name, pokemonId, mon["monsno"])
  # get_pokemon_name(555, True)
  # get_pokemon_tm_learnsets()
  # get_pokemon_stats("simisage", 512, 512)