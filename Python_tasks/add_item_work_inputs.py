import argparse
import json
import re
from pathlib import Path
from typing import Iterable


ADD_ITEM_PATTERN = re.compile(r"^_ADD_ITEM\s*\(([^)]*)\)")
LABEL_PATTERN = re.compile(r"^\s*([A-Za-z0-9_]+)\s*:\s*$")
LDVAL_PATTERN = re.compile(
    r"^_LDVAL\s*\(\s*(@[A-Za-z0-9_]+)\s*,\s*([+-]?\d+)\s*\)"
)
SCRIPT_DIRECTORIES = ("scriptdata", "vanillaScripts", "relumi_scripts")
OUTPUT_DIRECTORIES = {
    "scriptdata": "output",
    "vanillaScripts": "outputVanilla",
    "relumi_scripts": "3.0Output",
}


def scan_file(path: Path) -> list[tuple[str, int, list[str], int | None, int | None]]:
    """Find normal _ADD_ITEM calls whose ID and quantity are integer literals."""
    labels: list[tuple[str, list[tuple[int, str]]]] = []
    current_label = "<unknown>"
    current_lines: list[tuple[int, str]] = []

    with path.open("r", encoding="utf-8") as script_file:
        for line_number, line in enumerate(script_file, start=1):
            stripped_line = line.strip()
            label_match = LABEL_PATTERN.match(stripped_line)
            if label_match:
                if current_label != "<unknown>":
                    labels.append((current_label, current_lines))
                current_label = label_match.group(1)
                current_lines = []
            else:
                current_lines.append((line_number, stripped_line))

        if current_label != "<unknown>":
            labels.append((current_label, current_lines))

    matches: list[tuple[str, int, list[str], int | None, int | None]] = []
    for label_name, label_lines in labels:
        for line_number, line in label_lines:
            command_match = ADD_ITEM_PATTERN.match(line)
            if not command_match:
                continue

            arguments = [
                argument.strip()
                for argument in command_match.group(1).split(",")
            ]
            if (
                len(arguments) < 2
                or not arguments[0].isdigit()
                or not arguments[1].isdigit()
            ):
                continue

            matches.append(
                (
                    label_name,
                    line_number,
                    [],
                    int(arguments[0]),
                    int(arguments[1]),
                )
            )

    return matches


def iter_script_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".ev":
            yield path
        elif path.is_dir():
            yield from sorted(path.glob("*.ev"))


def scan_paths(
    paths: Iterable[Path],
) -> list[tuple[Path, str, int, list[str], int | None, int | None]]:
    results = []
    for path in iter_script_files(paths):
        for label, line_number, work_arguments, resolved_id, resolved_quantity in scan_file(
            path
        ):
            results.append(
                (
                    path,
                    label,
                    line_number,
                    work_arguments,
                    resolved_id,
                    resolved_quantity,
                )
            )
    return results


def write_item_map(
    item_map_path: Path,
    matches: Iterable[
        tuple[Path, str, int, list[str], int | None, int | None]
    ],
) -> None:
    """Merge resolved work-argument results into the existing item-map format."""
    if item_map_path.exists():
        with item_map_path.open("r", encoding="utf-8") as item_map_file:
            item_map = json.load(item_map_file)
    else:
        item_map = {}

    for path, label, _line_number, _work_arguments, resolved_id, resolved_quantity in matches:
        if resolved_id is None or resolved_quantity is None:
            continue

        room_name = path.stem
        room_entries = item_map.setdefault(room_name, [])
        entry = {
            "id": resolved_id,
            "quantity": resolved_quantity,
            "label_name": label,
        }
        if entry not in room_entries:
            room_entries.append(entry)

    item_map_path.parent.mkdir(parents=True, exist_ok=True)
    with item_map_path.open("w", encoding="utf-8") as item_map_file:
        json.dump(item_map, item_map_file, indent=4)
        item_map_file.write("\n")


def write_item_maps(
    repository_root: Path,
    matches: Iterable[
        tuple[Path, str, int, list[str], int | None, int | None]
    ],
    item_map_override: Path | None = None,
) -> dict[Path, int]:
    """Write each source script tree's matches to its configured output map."""
    matches_by_map: dict[Path, list[tuple[Path, str, int, list[str], int | None, int | None]]] = {}
    for match in matches:
        source_path = match[0]
        if item_map_override is not None:
            item_map_path = item_map_override
        else:
            source_directory = next(
                (
                    parent.name
                    for parent in source_path.parents
                    if parent.name in OUTPUT_DIRECTORIES
                ),
                None,
            )
            if source_directory is None:
                raise ValueError(
                    f"Cannot determine output map for script outside configured directories: {source_path}"
                )
            item_map_path = (
                repository_root
                / "Python_tasks"
                / OUTPUT_DIRECTORIES[source_directory]
                / "item_map.json"
            )
        matches_by_map.setdefault(item_map_path, []).append(match)

    for item_map_path, map_matches in matches_by_map.items():
        write_item_map(item_map_path, map_matches)

    return {item_map_path: len(map_matches) for item_map_path, map_matches in matches_by_map.items()}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find raw _ADD_ITEM calls whose first or second argument is a work value."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="One or more .ev files or directories. Defaults to all script directories.",
    )
    parser.add_argument(
        "--item-map",
        type=Path,
        help="Write all matches to this JSON file instead of routing by source directory.",
    )
    args = parser.parse_args()

    repository_root = Path(__file__).resolve().parent.parent
    selected_paths = args.paths or [
        repository_root / directory for directory in SCRIPT_DIRECTORIES
    ]
    matches = scan_paths(selected_paths)
    output_counts = write_item_maps(repository_root, matches, args.item_map)

    if not matches:
        print("No raw _ADD_ITEM work arguments found.")
        return

    for item_map_path, match_count in output_counts.items():
        print(f"Wrote {match_count} matches to {item_map_path}")

    for path, label, line_number, work_arguments, resolved_id, resolved_quantity in matches:
        argument_names = ", ".join(work_arguments)
        print(
            f"{path.relative_to(repository_root)}:{line_number} "
            f"label={label} work_arguments={argument_names} "
            f"id={resolved_id} quantity={resolved_quantity}"
        )


if __name__ == "__main__":
    main()
