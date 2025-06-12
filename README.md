# Gamedata repo

## Gather the data (Relumi)

1. Pull latest Romhack_Unity
2. Delete the existing AssetBundles in Romhack_Unity repo
3. Run the Build command in Unity
4. Unpack the following files
    - common_msbt
    - english
    - gamesettings
    - masterdatas
    - personal_masterdatas
5. Update all the files in Gamedata (detailed in the load_files file)
6. Copy all of the Assets/ExtraData/MonData/TMLearnset jsons to the TMLearnset folder in Gamedata

## Updating the Websites

1. Run the convert_lmpt_data script
2. Run the pokedex_generator script
3. Run the trainerDocsUtils script
2.0 version
```python
python3 Python_tasks/pokedex_generator.py
python3 Python_tasks/convert_lmpt_data.py
python3 Python_tasks/trainerDocsUtils.py
```
3.0 version
```python
python3 Python_tasks/pokedex_generator.py 3.0
python3 Python_tasks/convert_lmpt_data.py 3.0
python3 Python_tasks/trainerDocsUtils.py 3.0
```

## Updating the Dev Balance Data Work Sheets
(Only in ReLumi)

1. Run the pokedex_generator script with 3.0
```python
python3 Python_tasks/pokedex_generator.py
```
2. File > Import the pokedex.csv in Python_tasks/3.0Debug
    - Make sure to do "Insert new Sheet"
3. Delete the Held Item columns from the new sheet
4. Highlight everything except the column headers
5. Copy and paste that into the existing pokedex tab

## Checking Egg Moves

Adds the verification for all egg moves if they are attainable and how they would be attainable. This is ONLY checking if a pokemon can obtain a given move through breeding. Eventually I will add a way to check the level-up and tm moves as well.

To run the script, open the terminal and navigate to the gamedata repo. From there c/p this line into the terminal and press enter: 

```python
python3 Python_tasks/pokedex_generator.py
```

## Checking Valid Abilities

Check for valid abilities on all trainers. A valid ability is an ability that a pokemon has access to in their set of 3 abilities; ability 1, ability 2 and their hidden ability. If one of those abilities isn't specified, the game will then generate a random ability for the pokemon to have.

```python
python3 Python_tasks/trainerDocsUtils.py
```

## PokeApi searches to base Nat Dex Mons off of.

In order to use this, you need to have `python 3.11.4` installed. Then you will need to install [pokebase](https://github.com/PokeAPI/pokebase) with `pip install pokebase`.
To run the command, use `python3 Python_tasks/pokeapi_access.py 3.0`.

With this command, you will get the following output for each pokemon:
```json
{
  "name": "serperior",
  "id": 497,
  "abilities": [
    65,
    126
  ],
  "types": [
    "grass"
  ],
  "height": 33,
  "weight": 630,
  "stats": {
    "hp": 75,
    "attack": 75,
    "defense": 95,
    "special-attack": 75,
    "special-defense": 95,
    "speed": 113
  },
  "gender_ratio": 31,
  "held_items": [],
  "egg_groups": [
    5,
    7
  ],
  "tm_learnset": [
    347,
    ...
  ],
  "tm_bitfields": [
    14392912,
    136323843,
    541067344,
    7
  ]
}
```

Some things to note about this structure:
 - The name will not match the name in BDSP as it has been slugged and the order of some names has been changed.
 - The `id` will mostly not match the `pokemonId` in BDSP as this is the `id` obtained from PokeApi. However, the files are named with the `pokemonId` from BDSP so you can use that. The naming scheme is `{pokemonId}_stats.json`
