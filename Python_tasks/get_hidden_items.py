import json
import os
import re
import sys

import constants


repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
placedata_file_path = os.path.join(
    repo_file_path, "placedatas", constants.PLACEDATA_PATH
)
script_file_path = os.path.join(repo_file_path, constants.SCRIPT_DATA)
python_tasks_path = os.path.join(repo_file_path, "Python_tasks")
output_path = os.path.join(python_tasks_path, constants.OUTPUT_NAME)
zone_grid_file_path = os.path.join(
    python_tasks_path, "Resources", "sinnoh_zone_ids.txt"
)

AREA_ZONE_IDS = {
    "A01": {0, 346, 354, 355, 356, 357, 403, 404, 422, 429, 485},
    "A02": {38, 362, 364},
    "A03": {54, 197, 199, 201, 358, 359, 361, 377, 438},
    "A04": {74, 365},
    "A05": {367, 373, 375, 378, 394, 446, 456},
    "A06": {123},
    "A07": {110, 379, 383},
    "A08": {142, 167, 285, 411, 486, 490},
    "A09": {159, 351, 395, 397},
    "A10": {24, 257, 298, 332, 400},
    "A12": {259, 412, 414, 465, 487},
    "A13": {347, 352, 385, 392, 407},
    "A14": {186, 416, 420, 473, 489},
}


def load_zone_grid():
    with open(zone_grid_file_path, "r", encoding="utf-8") as grid_file:
        zone_ids = [int(value) for value in grid_file.read().split()]

    expected_count = 30 * 30
    if len(zone_ids) != expected_count:
        raise ValueError(
            f"Expected {expected_count} zone IDs in {zone_grid_file_path}, "
            f"found {len(zone_ids)}"
        )

    return zone_ids


def get_zone_id_from_position(position, zone_grid):
    x = int(position["x"])
    y = int(position["y"])
    if not 0 <= x < 30 * 32 or not 0 <= y < 30 * 32:
        return None

    grid_x = x // 32
    grid_y = y // 32
    return zone_grid[grid_y * 30 + grid_x]


def get_scripted_item_data(item_prefix):
    item_data = {}
    label_pattern = re.compile(r"^([A-Za-z0-9_]+):$")
    value_pattern = re.compile(
        r"^_LDVAL\(@SCWK_PARAM([01]),\s*(\d+)\)\s*$"
    )
    field_item_pattern = re.compile(r"^_FLD_ITEM_EVENT\((\d+),\s*(\d+)\)")

    for filename in os.listdir(script_file_path):
        if not filename.endswith(".ev"):
            continue

        file_path = os.path.join(script_file_path, filename)
        with open(file_path, "r", encoding="utf-8") as script_file:
            lines = script_file
            current_label = None
            current_values = {}

            def save_current_label():
                if current_label and current_label.startswith(item_prefix):
                    if item_prefix == "ev_fld_item":
                        if "itemId" in current_values and "quantity" in current_values:
                            item_data[current_label] = current_values.copy()
                        return
                    if 0 in current_values and 1 in current_values:
                        item_data[current_label] = {
                            "itemId": current_values[0],
                            "quantity": current_values[1],
                        }

            for line in lines:
                stripped_line = line.strip()
                label_match = label_pattern.fullmatch(stripped_line)
                if label_match:
                    save_current_label()
                    current_label = label_match.group(1)
                    current_values = {}
                    continue

                value_match = value_pattern.fullmatch(stripped_line)
                if current_label and value_match:
                    current_values[int(value_match.group(1))] = int(
                        value_match.group(2)
                    )
                    continue

                field_item_match = field_item_pattern.match(stripped_line)
                if current_label and field_item_match:
                    current_values["itemId"] = int(field_item_match.group(1))
                    current_values["quantity"] = int(field_item_match.group(2))

            save_current_label()

    return item_data


def get_hidden_items(item_mode="hidden"):
    item_prefix = "ev_fld_item" if item_mode == "field" else "ev_hide_item"
    hidden_items = {}
    scripted_item_data = get_scripted_item_data(item_prefix)
    zone_grid = load_zone_grid()

    for filename in os.listdir(placedata_file_path):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(placedata_file_path, filename)
        with open(file_path, "r", encoding="utf-8") as placedata_file:
            placedata = json.load(placedata_file)

        area_match = re.fullmatch(r"PlaceData_(A\d{2})\.json", filename)
        area_name = area_match.group(1) if area_match else None

        for event in placedata.get("Data", []):
            talk_label = event.get("ID", "")
            if talk_label == "":
                talk_label = event.get("TalkLabel", "")
            # if not talk_label.startswith(item_prefix):
            #     continue
            # if item_mode != "field" and constants.GAME_MODE == constants.GAME_MODE_3:
            #     # Relumi uses the sparkle OGI for hidden items, while Vanilla and Lumi uses -1
            #     if event.get("ObjectGraphicIndex") != 579:
            #         continue
            # elif item_mode != "field":
            #     if event.get("ObjectGraphicIndex") != -1:
            #         continue

            position = event["Position"]
            zone_id = event["zoneID"]
            if area_name is not None:
                looked_up_zone_id = get_zone_id_from_position(position, zone_grid)
                if looked_up_zone_id is None:
                    print(
                        f"Placedata {talk_label} in {filename} has coordinates "
                        f"outside the 0-959 grid: ({position['x']}, {position['y']})"
                    )
                else:
                    stored_zone_id = zone_id
                    if stored_zone_id != looked_up_zone_id:
                        print(
                            f"ZoneID mismatch for {talk_label} in {filename}: "
                            f"placedata has {stored_zone_id}, coordinate lookup "
                            f"gives {looked_up_zone_id} at "
                            f"({position['x']}, {position['y']})"
                        )
                    zone_id = looked_up_zone_id
                    allowed_zone_ids = AREA_ZONE_IDS.get(area_name)
                    if (
                        allowed_zone_ids is not None
                        and zone_id not in allowed_zone_ids
                    ):
                        print(
                            f"Item {talk_label} in {filename} is outside "
                            f"area {area_name}: computed zoneID {zone_id} at "
                            f"({position['x']}, {position['y']})"
                        )

            zone_id = str(zone_id)
            hidden_items.setdefault(zone_id, []).append(
                {
                    "TalkLabel": talk_label,
                    **scripted_item_data.get(talk_label, {}),
                    "Position": {
                        "x": position["x"],
                        "y": position["y"],
                    },
                }
            )

    return hidden_items


def main():
    item_mode = sys.argv[2] if len(sys.argv) > 2 else "hidden"
    if item_mode not in {"hidden", "field"}:
        raise ValueError("Item mode must be 'hidden' or 'field'")

    items = get_hidden_items(item_mode)
    output_name = "field_items.json" if item_mode == "field" else "hidden_items.json"
    output_file_path = os.path.join(output_path, output_name)
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        json.dump(items, output_file, indent=4)
        output_file.write("\n")

    print(f"Wrote {sum(map(len, items.values()))} {item_mode} items to {output_file_path}")


if __name__ == "__main__":
    main()