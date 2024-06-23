import json
import os
import copy
import constants

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, "input")
input_file_path3 = os.path.join(parent_file_path, "3.0Input")
output_file_path = os.path.join(parent_file_path, "Python_tasks", constants.OUTPUT_NAME)

personal_data_path = os.path.join(input_file_path, 'PersonalTable.json')
personal_data_path3 = os.path.join(input_file_path3, 'PersonalTable.json')

form_name_path = os.path.join(input_file_path, 'english_ss_zkn_form.json')
form_name_path3 = os.path.join(input_file_path3, 'english_ss_zkn_form.json')

new_to_old_personal_ids = {}
NEW_FORM_MAP = {}
OLD_FORM_MAP = {}

with open(personal_data_path3, mode="r", encoding="utf-8") as new_f, open(personal_data_path, mode="r", encoding="utf-8") as old_f:
  new_personal_data = json.load(new_f)
  old_personal_data = json.load(old_f)

  for curr in new_personal_data['Personal']:
    if curr['monsno'] not in NEW_FORM_MAP:
      NEW_FORM_MAP[curr['monsno']] = []
    NEW_FORM_MAP[curr['monsno']].append(curr['id'])

  for curr in old_personal_data['Personal']:
    if curr['monsno'] not in OLD_FORM_MAP:
      OLD_FORM_MAP[curr['monsno']] = []
    OLD_FORM_MAP[curr['monsno']].append(curr['id'])

  for pokemonId, personal_item in enumerate(new_personal_data["Personal"]):
    new_mons_no = personal_item["monsno"]
    new_form_no = NEW_FORM_MAP[new_mons_no].index(pokemonId)
    if new_mons_no in OLD_FORM_MAP:
      if (len(OLD_FORM_MAP[new_mons_no])) <= new_form_no:
        continue
      new_to_old_personal_ids[pokemonId] = OLD_FORM_MAP[new_mons_no][new_form_no]
    else:
      continue

with open(form_name_path3, mode="r", encoding="utf-8") as new_name_f, open(form_name_path, mode="r+", encoding="utf-8") as old_name_f:
  new_name_data = json.load(new_name_f)
  old_name_data = json.load(old_name_f)
  copy_name_data = copy.deepcopy(old_name_data)

  for new_personal_id, old_personal_id in new_to_old_personal_ids.items():
    new_mons_name = new_name_data["labelDataArray"][new_personal_id]["wordDataArray"][0]["str"]
    old_mons_name = old_name_data["labelDataArray"][old_personal_id]["wordDataArray"][0]["str"]
    if not old_mons_name and new_mons_name != old_mons_name:
      old_mons_name = "NOTHING HERE ORIGINALLY"
    if new_mons_name != old_mons_name:
      print("Old Name:", old_mons_name, "New Name:", new_mons_name)
      copy_name_data["labelDataArray"][old_personal_id]["wordDataArray"][0]["str"] = new_mons_name

  with open(os.path.join(output_file_path, 'english_ss_zkn_form.json'), 'w') as output:
    output.write(json.dumps(copy_name_data, indent=2))