import pokebase
import json
import os
import sys

import constants
import poke_api_constants
from load_files import load_data
from pokemonUtils import get_pokemon_name, slugify

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

def get_pokemon_stats(pokemon_name, pokemonId, monsno, counter=0):
  form = None
  pokemon = None
  species = None
  form_name = pokemon_name
  species_name = pokemon_name
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
    pokemon_stats = {
      "name": form.name if form else pokemon.name,
      "id": pokemon.id,
      "abilities": [ability.ability.name for ability in pokemon.abilities],
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
          "held_item": item.item.name,
          "rarity": next((vd.rarity for vd in item.version_details if vd.version.name == "platinum"), None)
        }
        for item in pokemon.held_items
      ],
      "egg_groups": [
        poke_api_constants.EGG_GROUPS[egg_group.name]
        for egg_group in species.egg_groups
      ]
    }

    # Write the dictionary to a JSON file
    file_name = f"{pokemonId}_stats.json"
    with open(os.path.join(stats_file_path, file_name), "w", encoding="utf-8") as json_file:
      json.dump(pokemon_stats, json_file, ensure_ascii=False, indent=2)

    log_success(f"Stats for {form_name} written to {file_name}")
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