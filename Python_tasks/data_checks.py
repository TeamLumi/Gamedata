import copy
from pokemonUtils import get_form_pokemon_personal_id, get_form_name, get_pokemon_name
from load_files import load_data

full_data = load_data()

def bad_encounter_data(pkmn_name, routeName, route):
    bad_encounters = []
    print('BAD ENCOUNTER', pkmn_name, routeName, route)
    bad_encounters.append({pkmn_name, routeName, route})
    return bad_encounters

def check_bad_encounter(encounters, tracker_route, pkmn_key, lumi_formula_mon, temp_form_no, zoneID, method=''):
    pokedex, name_routes, diff_forms = ( full_data["pokedex"], full_data['name_routes'], full_data['diff_forms'])

    bad_encounters = []
    bad_encounter_list = ["Gigantamax", "Eternamax", "Mega ", "Totem "]
    pokemonPersonalId = get_form_pokemon_personal_id(lumi_formula_mon, temp_form_no)

    if pokemonPersonalId is not None and any(substring in get_pokemon_name(pokemonPersonalId) for substring in bad_encounter_list):
        bad_encounters.append(bad_encounter_data(get_pokemon_name(pokemonPersonalId), name_routes[tracker_route], zoneID))
        return bad_encounters
    elif pkmn_key not in diff_forms.keys():
        bad_encounters.append(bad_encounter_data(pokedex[str(lumi_formula_mon)], name_routes[tracker_route], zoneID))
        return bad_encounters
    elif method == "Tracker":
        encounters[str(tracker_route)].append(diff_forms[pkmn_key][1])
        return -1
    else:
        return -2

def check_mons_list(pokemon_list, zoneID, final_list):
    original_list = []
    missing_list = []
    radar_count = 0
    radar_list = {zoneID: []}

    for mon in pokemon_list:
        if mon[1] == 'ground_mons' or mon[1] == 'day' or mon[1] == 'night':
            original_list.append(mon[0])
    active_list = copy.deepcopy(original_list)

    active_list[9] = active_list[1]
    active_list[10] = active_list[4]
    active_list[11] = active_list[5]
    for mon in pokemon_list:
        if mon[1] == 'swayGrass':
            radar_list[zoneID].append(get_pokemon_name(mon[0]))
            active_list[1] = mon[0]
        if mon[1].startswith('gba') and mon[2] != 2 and radar_count < 2:
            radar_count += 1
            if radar_count == 1:
                active_list[4] = mon[0]
            if radar_count == 2:
                active_list[5] = mon[0]
    for mon in original_list:
        if mon == 0:
            continue
        pokemon_name = get_pokemon_name(mon)
        if mon not in active_list:
            missing_list.append(pokemon_name)

    unique_radar_list = list(set(radar_list[zoneID]))
    if len(unique_radar_list) > 1:
        print(radar_list)
    unique_list = list(set(missing_list))
    if len(unique_list) > 0:
        return unique_list
    return -1
