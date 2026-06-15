import json
import os
import re


def consolidate_tmlearnset():
    """
    Consolidates all individual TMLearnset JSON files into a single file.
    Format: { monsno: { formno_0: data, formno_1: data, ... } }
    """
    # Define paths
    tmlearnset_folder = os.path.join(os.path.dirname(__file__), '..', 'TMLearnset')
    output_file = os.path.join(os.path.dirname(__file__), '..', '3.0Input', 'TMLearnset_consolidated.json')

    # Dictionary to store consolidated data
    consolidated_data = {}

    # Iterate through all JSON files in the TMLearnset folder
    for filename in sorted(os.listdir(tmlearnset_folder)):
        if filename.endswith('.json'):
            # Extract monsno and formno from filename using regex
            match = re.match(r'monsno_(\d+)_formno_(\d+)\.json', filename)
            if match:
                monsno = match.group(1)
                formno = match.group(2)

                # Read the file
                file_path = os.path.join(tmlearnset_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)

                # Initialize monsno entry if it doesn't exist
                if monsno not in consolidated_data:
                    consolidated_data[monsno] = {}

                # Add formno data
                consolidated_data[monsno][f'formno_{formno}'] = file_data

    # Sort the dictionary by monsno (as integers)
    sorted_consolidated_data = {}
    for monsno in sorted(consolidated_data.keys(), key=int):
        sorted_consolidated_data[monsno] = consolidated_data[monsno]

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_consolidated_data, f, indent=2)

    print(f"Successfully consolidated {len(consolidated_data)} Pokémon entries into {output_file}")
    print(f"Total files processed: {sum(len(forms) for forms in consolidated_data.values())}")


if __name__ == "__main__":
    consolidate_tmlearnset()
