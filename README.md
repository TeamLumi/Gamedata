Gamedata repo

Adds the verification for all egg moves if they are attainable and how they would be attainable. To run the script, open the terminal and navigate to the gamedata repo. From there c/p this line into the terminal and press enter: 

```python
python3 Python_tasks/pokedex_generator.py
```

- Added PokeApi searches to base Nat Dex Mons off of.

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
