from load_files import load_data

def get_first_evo_pokemon_id(pokemonId):
  evolutionData = full_data['evolution_dex']
  if str(pokemonId) not in evolutionData.keys():
    print("This pokemon is not in the evolution Data", pokemonId)
    return -1
  return evolutionData[str(pokemonId)]["path"][0]

if __name__ != "__main__":
  full_data = load_data()