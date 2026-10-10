import os
import re
import json
import constants

# This script should work, but haven't tested yet.
repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
script_path = os.path.join(repo_file_path, constants.SCRIPT_DATA)
python_tasks_path = os.path.join(repo_file_path, "Python_tasks")
output_path = os.path.join(python_tasks_path, constants.OUTPUT_NAME)
filenames = []
for filename in os.listdir(script_path):
    if os.path.isfile(os.path.join(script_path, filename)):
        filenames.append(filename)

if constants.GAME_MODE == constants.GAME_MODE_VANILLA or constants.GAME_MODE == constants.GAME_MODE_2:
    item_event_keyword = "_CHG_COMMON_SCR('ev_item_event_keywait')"
else:
    item_event_keyword = "_CALL('ev_item_event')"
parameter_regex = r'\([^,]*,\s*(.*?)\)'
item_data = {}

special_cases = {
    'ev_d26r0104_item_event_ok': [
        {'id': 1, 'quantity': 1, 'label_name': 'ev_d26r0104_item_event_ok'},
    ],
    'ev_tower_gate_talk_prize_get': [],
    'ev_tower_gate_return_prize_get': [],
    'ev_tower_gate_prize_get': [],
    'ev_tower_gate_prize_get_10_loop': [],
    'ev_tower_gate_prize_get_20': [],
    'ev_r221r0101_item_add': [
        {
            "id": 149,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 150,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 151,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 152,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 153,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 154,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 155,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 156,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 159,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 160,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 161,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 162,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 163,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 164,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 165,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 166,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 167,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 168,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 157,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 158,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 169,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 170,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 171,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 172,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 173,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        },
        {
            "id": 174,
            'quantity': 1,
            'label_name': "ev_r221r0101_item_add"
        }
    ],

    # These ones are only for Lumi
    'ev_turearuki_poke_item_get': [{'id': 0, 'quantity': 1, 'label_name': 'ev_turearuki_poke_item_get'}],
    'ev_d01r0102_leader_01_stone': [
        {'id': 80, 'quantity': 1, 'label_name': 'ev_d01r0102_leader_01_stone'},
        {'id': 81, 'quantity': 1, 'label_name': 'ev_d01r0102_leader_01_stone'},
        {'id': 82, 'quantity': 1, 'label_name': 'ev_d01r0102_leader_01_stone'},
        {'id': 83, 'quantity': 1, 'label_name': 'ev_d01r0102_leader_01_stone'},
        {'id': 84, 'quantity': 1, 'label_name': 'ev_d01r0102_leader_01_stone'},
        {'id': 85, 'quantity': 1, 'label_name': 'ev_d01r0102_leader_01_stone'},
        {'id': 849, 'quantity': 1, 'label_name': 'ev_d01r0102_leader_01_stone'}
    ],

    # These ones are only for ReLumi
    'ev_d11r0101_present_kinomi_set_03': [],
}

ldval_map = {
    'ev_c01r0201_kuji_no_4': '_LDVAL(@SCWK_PARAM3,',
    'ev_c01r0201_kuji_no_3': '_LDVAL(@SCWK_PARAM3,',
    'ev_c01r0201_kuji_no_2': '_LDVAL(@SCWK_PARAM3,',
    'ev_c01r0201_kuji_no_1': '_LDVAL(@SCWK_PARAM3,',
    'ev_c01r0201_kuji_no_0': '_LDVAL(@SCWK_PARAM3,',
    'common_vm_03': '_LDVAL(@SCWK_PARAM1,',
    'ev_c10r0101_tm_handler_common_no_flag': '_LDVAL(@SCWK_TEMP0,',
    'ev_c10r0101_tm_handler_common': '_LDVAL(@SCWK_TEMP0,',
    'ev_c01r0201_kuji_item_get_chk': '_LDWK(@SCWK_TEMP0,',
    'ev_turearuki_poke_item_get': '_LDVAL(@SCWK_TEMP0,',
    'ev_tower_gate_prize_get_common': '_LDWK(@SCWK_TEMP0,',
    'r209_fishing1_yes': '_LDVAL(@SCWK_TEMP0,',
    'r218r0101_fishing_yes': '_LDVAL(@SCWK_TEMP0,',
    'ev_item_fanatic_give_item': '_LDVAL(@SCWK_TEMP0,',
    'ev_item_fanatic_give_item_two': '_LDVAL(@SCWK_TEMP0,'
}

def get_indices(file_lines, pattern):
    return [
        index
        for index, value in enumerate(file_lines)
        if re.search(pattern, value)
    ]

def remove_after_semicolon(input_string):
    result_string = input_string.split(';')[0]
    return result_string.strip()

def extract_label_ldval(label_name, file_lines):
    label_index = next(
        (
            index
            for index, value in enumerate(file_lines)
            if value == f'{label_name}:'
        ),
        None
    )
    if label_index is None:
        return None

    for value in file_lines[label_index + 1:]:
        if value.endswith(':'):
            break
        match = re.search(r'_LDVAL\([^,]+,\s*(\d+)\)', value)
        if match:
            return int(match.group(1))

    return None

def find_jumped_value(function_name, file_lines, ldval_command, room_name):
    item_ids = []
    indices = get_indices(
        file_lines,
        rf"_JUMP\(\s*['\"]{re.escape(function_name[:-1])}['\"]\s*\)"
    )

    if len(indices) == 0:
        indices = get_indices(
            file_lines,
            rf"_CALL\(\s*['\"]{re.escape(function_name[:-1])}['\"]\s*\)"
        )

    if len(indices) == 0:
        indices = get_indices(
            file_lines,
            rf"_CASE_JUMP\(\s*[^,]+,\s*['\"]{re.escape(function_name[:-1])}['\"]\s*\)"
        )
    if len(indices) == 0:
        if function_name[:-1] in special_cases.keys():
            return special_cases[function_name[:-1]]
        raise Exception(function_name)
    for index in indices:
        command_start_index = find_closest_previous_index(file_lines, index, ':')
        ldval_map_command = 0
        if file_lines[command_start_index][:-1] in ldval_map.keys():
            ldval_map_command = ldval_map[file_lines[command_start_index][:-1]]
        else:
            ldval_map_command = ldval_command
        print(f"Finding jumped value for label: {file_lines[command_start_index][:-1]} with ldval command: {ldval_map_command}")
        item_ids.extend(extract_item_id(command_start_index, index, file_lines, room_name))
    return item_ids

def get_normal_item_id(item_id_command):
    match = re.search(r'\b\d+\b', item_id_command)
    if match:
        return int(match.group())
    raise Exception(item_id_command)

def extract_item_id(command_start_index, ldval_index, file_lines, room_name):
    print(f"Extracting item id for label: {file_lines[command_start_index][:-1]} in room: {room_name}")
    item_ids = []
    extracted_lines = file_lines[command_start_index:ldval_index + 1]
    label_name = extracted_lines[0][:-1]
    # Remove anything after a semicolon in the extracted lines
    item_id_commands = [remove_after_semicolon(value) for index, value in enumerate(extracted_lines) if value.startswith("_LDVAL(@SCWK_TEMP0") or value.startswith("_LDWK(@SCWK_TEMP0")]
    item_quantity_commands = [remove_after_semicolon(value) for index, value in enumerate(extracted_lines) if value.startswith("_LDVAL(@SCWK_TEMP1") or value.startswith("_LDWK(@SCWK_TEMP1")]
    if label_name in special_cases.keys():
        return special_cases[label_name]
    if len(item_id_commands) == 0:
        direct_item_id = extract_label_ldval(label_name, file_lines)
        print(f"Direct item id for label: {label_name} in room: {room_name} is: {direct_item_id}")
        if direct_item_id is not None:
            return [{
                'id': direct_item_id,
                'quantity': 1,
                'label_name': label_name
            }]

        ldval_map_command = ldval_map[label_name] if label_name in ldval_map.keys() else None
        print(f"Finding jumped value for label: {label_name} with ldval command: {ldval_map_command}")
        item_ids.append({
            'id': find_jumped_value(extracted_lines[0], file_lines, ldval_map_command, room_name),
            'quantity': 1,
            'label_name': label_name
        })
    for index, item_id_command in enumerate(item_id_commands):
        item_qty = item_quantity_commands[index] if index < len(item_quantity_commands) else 1
        print(f"Extracting item id for label: {label_name} in room: {room_name} with command: {item_id_command} and quantity command: {item_qty}")
        item_qty_value = re.search(parameter_regex, item_qty).group(1) if item_qty != 1 else 1
        counted_chars = item_id_command.count('@')
        if counted_chars == 1:
            item_ids.append({
                'id': get_normal_item_id(item_id_command),
                'quantity': int(item_qty_value),
                'label_name': label_name
            })
        elif counted_chars == 2:
            work_value = re.search(parameter_regex, item_id_command).group(1)
            print(f"Finding jumped value for label: {label_name} with work value: {work_value}")
            ldval_command = f"_LDVAL({work_value},"
            item_ids.append({
                'id': find_jumped_value(extracted_lines[0], file_lines, ldval_command, room_name),
                'quantity': int(item_qty_value),
                'label_name': label_name
            })
        else:
            print('Whoops')

    return item_ids

def find_closest_previous_index(array, start_index, target_character):
    for i in range(start_index - 1, -1, -1):
        if target_character in array[i]:
            return i
    return None

def find_item_id(file_lines, room_name):
    item_ids = []
    item_event_keyword_indices = [index for index, value in enumerate(file_lines) if value == item_event_keyword]
    for ldval_index in item_event_keyword_indices:
        command_start_index = find_closest_previous_index(file_lines, ldval_index, ':')
        new_item_ids = extract_item_id(command_start_index, ldval_index, file_lines, room_name)
        print(f"Found item ids for room {room_name}: {new_item_ids}")
        item_ids.extend(new_item_ids)
    return item_ids

for filename in filenames:
    file_path = os.path.join(script_path, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_data = file.read()
            room_name = filename.replace('.ev', '')
            data_lines = file_data.split('\n')
            file_lines = [s.strip() for s in data_lines]
            items = find_item_id(file_lines, room_name)
            if len(items) > 0:
                item_data[room_name] = items

file_path = os.path.join(output_path, "item_map.json")

with open(file_path, 'w') as json_file:
    json.dump(item_data, json_file, indent=4)