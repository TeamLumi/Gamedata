import json
import os

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
resource_file_path = os.path.join(repo_file_path, "Python_tasks", "Resources")

with open(os.path.join(resource_file_path, 'fullLearnset.json'), "r", encoding="utf-8") as input:
  data = json.load(input)
  # Convert the data to an object with "id"s as keys
  pokemon_data = {str(item['id']): {k: v for k, v in item.items() if k != 'id'} for item in data}

  # Convert the object back to JSON format

  # Print or write the formatted JSON to a file
with open(os.path.join(resource_file_path, 'fullLearnset.json'), "w", encoding="utf-8") as output:
  json.dump(pokemon_data, output, ensure_ascii=False, indent=2)