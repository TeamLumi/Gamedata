import os
import re
import json

from trainerUtils import process_files
import constants

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
parent_file_path = os.path.abspath(os.path.dirname(__file__))
debug_file_path = os.path.join(parent_file_path, constants.DEBUG_NAME)

shop_items = {}

def parse_item_ev_file(file_path):
  """
  The purpose of this function is to parse a text file and find every instance of the substring _TRAINER_BTL_SET or _TRAINER_MULTI_BTL_SET.
  """

  with open(file_path, 'r', encoding="utf-8") as f:
    for line in f:
      substrings = line.split('\n')
      for substring in substrings:
        zone_code = file_path.split("/")[-1].split(".")[0]
        if zone_code.upper() == constants.EVE_AREA_NAME:
          zone_code = "t04"

        if constants.FIXED_SHOP in substring:
          match = re.search(constants.FIXED_SHOP_PATTERN, substring)
          if match and zone_code not in shop_items.keys():
            shop_items[zone_code] = [match[1]]
          elif match and zone_code in shop_items.keys():
            shop_items[zone_code].append(match[1])
    with open(os.path.join(debug_file_path, 'fixed_shop.json'), 'w', encoding='utf-8') as f:
        json.dump(shop_items, f, indent=2)
    return shop_items

if __name__ == "__main__":
  process_files(os.path.join(repo_file_path, "scriptdata"), parse_item_ev_file, trainer_mode=False)