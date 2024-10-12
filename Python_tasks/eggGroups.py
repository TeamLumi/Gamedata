import constants
from load_files import load_data

def createPokemonByEggGroupMap(pokemonMap, currentPokemon):
    # Use sets so I don't have to handle duplicates, looking at you Unown
    if currentPokemon['egg_group1'] not in pokemonMap:
        pokemonMap[currentPokemon['egg_group1']] = set()

    if currentPokemon['egg_group2'] not in pokemonMap:
        pokemonMap[currentPokemon['egg_group2']] = set()

    pokemonMap[currentPokemon['egg_group1']].add(currentPokemon['id'])
    pokemonMap[currentPokemon['egg_group2']].add(currentPokemon['id'])
    return pokemonMap

def pokemonIdsByEggGroup(POKEMON_IDS_BY_EGG_GROUP):
  for pokemon in PersonalTable['Personal']:
    createPokemonByEggGroupMap(POKEMON_IDS_BY_EGG_GROUP, pokemon)

def getEggGroupViaPokemonId(pokemonId=0):
    if not isinstance(pokemonId, int) or pokemonId < 0 or pokemonId >= len(PersonalTable['Personal']):
        raise ValueError(f"Bad pokemonId: {pokemonId}")

    pokemonDetails = PersonalTable['Personal'][pokemonId]
    eggGroup1 = pokemonDetails['egg_group1']
    eggGroup2 = pokemonDetails['egg_group2']
    return [eggGroup1] if eggGroup1 == eggGroup2 else [eggGroup1, eggGroup2]

def getEggGroupNameById(eggGroupId=0):
    if not isinstance(eggGroupId, int) or eggGroupId < 0 or eggGroupId > constants.HIGHEST_EGG_GROUP_ID:
        raise ValueError(f"Bad eggGroupId: {eggGroupId}")
    return constants.EGG_GROUPS[eggGroupId]

def getPokemonIdsInEggGroup(eggGroupId=0):
    if not isinstance(eggGroupId, int) or eggGroupId < 0 or eggGroupId > constants.HIGHEST_EGG_GROUP_ID:
        raise ValueError(f"Bad eggGroupId: {eggGroupId}")
    return list(POKEMON_IDS_BY_EGG_GROUP.get(eggGroupId, set())) # Back to list for easier handling

if __name__ != "__main__":
  POKEMON_IDS_BY_EGG_GROUP = {}
  full_data = load_data()
  PersonalTable = full_data["personal_table"]
  POKEMON_IDS_IN_EGG_GROUP = pokemonIdsByEggGroup(POKEMON_IDS_BY_EGG_GROUP)