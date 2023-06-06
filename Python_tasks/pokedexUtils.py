import json
import os
from pokemonUtils import GenForms, get_pokemon_info, get_pokemon_name
from load_files import load_data

full_data = load_data()

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
debug_file_path = os.path.join(repo_file_path, "Python_tasks", "Debug")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")

def get_form_format(monsNo, formNo):
    mon_zeros = 3 - len(str(monsNo))
    form_zeros = 3 - len(str(formNo))
    return f"ZKN_FORM_{mon_zeros*'0'}{monsNo}_{form_zeros*'0'}{formNo}"

def remove_duplicates(path_dictionary):
    new_path = []
    for path_element in path_dictionary:
        if path_element not in new_path:
            new_path.append(path_element)
    return new_path

def remove_duplicate_forms(evolve):
    for pokemon in evolve.keys():
        evolve[pokemon]["path"] = remove_duplicates(evolve[pokemon]["path"])

def add_forms(evolve, graph):
    forms = GenForms()
    for form in forms:
        form_num = forms[form]
        pokemon_id = int(form[-7:-4])
        evolve_array = graph[form_num]["ar"]
        for pokemon in evolve.keys():
            if int(pokemon) != pokemon_id:
                continue
            initial_evolution_path = evolve[pokemon]["path"]
            form_evo_path = evolve[form_num]["path"]
            first_form_evo = form_evo_path[0]

            for evolution in initial_evolution_path:
                if len(evolve_array) != 0:
                    continue
                if evolution in evolve[first_form_evo]["path"]:
                    evolve[evolution]["path"].append(form_num)
                if len(evolve[form_num]["path"]) < 2:
                    evolution_path = evolve[evolution]["path"] + form_evo_path
                    evolve[form_num]["path"] = remove_duplicates(evolution_path)
                    evolve[evolution]["path"] = remove_duplicates(evolution_path)

def start_pathfinding(evolve, graph):
    forms = GenForms()

    for pokemon in evolve.keys():
        queue = []
        queue.append(pokemon)
        queue.append(0)
        new_queue = []

        if pokemon not in evolve[pokemon]["path"]:
            evolve[pokemon]["path"].append(pokemon)

        while queue:
            current_mon = queue.pop(0)
            current_form = queue.pop(0)
            mon_zeros = 3 - len(str(current_mon))
            form_zeros = 3 - len(str(current_form))
            form_format = get_form_format(current_mon, current_form)
            if form_format in forms.keys():
                current_mon = forms[form_format]
            adjacent_nodes = graph[current_mon]["ar"]
            if len(adjacent_nodes) != 0:
                next_mon = adjacent_nodes[2]
                next_form = adjacent_nodes[3]
                form_format = get_form_format(next_mon, next_form)

                if form_format in forms.keys():
                    next_mon = forms[form_format]

                evolve[next_mon]["path"] = evolve[current_mon]["path"] + [next_mon]
                for i in range(2, len(adjacent_nodes), 5):
                    new_queue.append(adjacent_nodes[i])
                    new_queue.append(adjacent_nodes[i + 1])
                    while new_queue:
                        curr_mon = new_queue.pop(0)
                        curr_form = new_queue.pop(0)
                        form_format = get_form_format(curr_mon, curr_form)

                        if form_format in forms.keys():
                            curr_mon = forms[form_format]

                        ### This section is for the current pokemon
                        evolve[curr_mon]["path"].append(pokemon)
                        evolve[curr_mon]["path"].append(curr_mon)
                        evolve[curr_mon]["path"] = list(dict.fromkeys(evolve[curr_mon]["path"]))

                        ### This section is for the first pokemon in the chain
                        evolve[evolve[curr_mon]["path"][0]]["path"].append(curr_mon)
                        evolve[evolve[curr_mon]["path"][0]]["path"] = [x for i, x in enumerate(evolve[evolve[curr_mon]["path"][0]]["path"]) if x not in evolve[evolve[curr_mon]["path"][0]]["path"][:i]]

                        ### This section is for the second pokemon in the chain
                        if len(evolve[curr_mon]["path"]) > 1:
                            evolve[evolve[curr_mon]["path"][1]]["path"].append(curr_mon)
                            evolve[evolve[curr_mon]["path"][1]]["path"] = [x for i, x in enumerate(evolve[evolve[curr_mon]["path"][1]]["path"]) if x not in evolve[evolve[curr_mon]["path"][1]]["path"][:i]]

                        if len(evolve[curr_mon]["path"]) > 2:
                            evolve[evolve[curr_mon]["path"][2]]["path"].append(curr_mon)
                            evolve[evolve[curr_mon]["path"][2]]["path"] = [x for i, x in enumerate(evolve[evolve[curr_mon]["path"][2]]["path"]) if x not in evolve[evolve[curr_mon]["path"][2]]["path"][:i]]

                    ### Dewpider (751) currently evolves into Dewpider and creates an infinite loop
                    ### These can be taken away once that is fixed
                    if current_mon != 751:
                        new_queue.append(adjacent_nodes[i])
                        new_queue.append(adjacent_nodes[i + 1])

                if current_mon != 751:
                    queue.append(next_mon)
                    queue.append(next_form)

            if not queue:
                queue = new_queue
                new_queue = []
        for extra in evolve[pokemon]["path"]:
            for i in range(0, len(graph[extra]["ar"]), 5):
                evolve[pokemon]["method"].append(graph[extra]["ar"][i])
            evolve[pokemon]["ar"].append(graph[extra]["ar"])


def evolution_pathfinding():
    with open(os.path.join(input_file_path, 'EvolveTable.json'), "r", encoding="utf-8") as f:
        graphing = json.load(f)
    graph = graphing["Evolve"]
    forms = GenForms()
    evolve = {}
    for node in graph:
        evolve[node["id"]] = {"path": [], "method": [], "ar": []}

    start_pathfinding(evolve, graph)
    add_forms(evolve, graph)
    remove_duplicate_forms(evolve)

    with open(os.path.join(debug_file_path, "evolution.json"), "w", encoding = "utf-8") as output:
        json.dump(evolve, output, ensure_ascii=False, indent=2)
    return evolve

def get_mon_dex_info(pokemon, evolve):
    diff_forms = full_data['diff_forms']
    poke_info = get_pokemon_info(pokemon)
    poke_name = get_pokemon_name(pokemon)
    dex_info = {
        "value": pokemon,
        "text": poke_name,
        "type": poke_info["type"].upper()
        }
    if "dualtype" in poke_info.keys() and poke_info["dualtype"] != 0:
        dex_info["dualtype"] = poke_info["dualtype"].upper()
    dex_info["evolve"] = evolve
    dex_info["generation"] = 8
    dex_info["abilities"] = [poke_info['ability1'], poke_info['ability2'], poke_info['abilityH']]
    dex_info["dexNum"] = pokemon
    dex_info["form"] = 0
    if pokemon > 1010:
        for poke_form in diff_forms.keys():
            if poke_name in diff_forms[poke_form]:
                form_number = diff_forms[poke_form][4]
                og_num = diff_forms[poke_form][3]
        dex_info["dexNum"] = og_num
        dex_info["form"] = int(form_number)
        return dex_info

    return dex_info

def getPokedexInfo():
    pokedex = []
    evolutions = evolution_pathfinding()

    for pokemon in evolutions.keys():
        if pokemon >= 1456:
            continue
        evolve = evolutions[pokemon]["path"]
        if pokemon < 906 or pokemon > 1010:
            dex_info = get_mon_dex_info(pokemon, evolve)
        pokedex.append(dex_info)

    with open(os.path.join(output_file_path, "pokedex_info.json"), "w", encoding="utf-8") as output:
        json.dump(pokedex, output, ensure_ascii=False, indent=2)
    return pokedex

if __name__ == "__main__":
    getPokedexInfo()