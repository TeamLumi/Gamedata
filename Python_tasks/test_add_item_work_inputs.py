import json
import tempfile
import unittest
from pathlib import Path

from Python_tasks.add_item_work_inputs import scan_file, write_item_map


class AddItemWorkInputsTests(unittest.TestCase):
    def test_scans_normal_integer_add_item_calls(self):
        source = """ev_sample:
    _ADD_ITEM(20, 5, @SCWK_ANSWER)
    _ADD_ITEM(@SCWK_TEMP0, @SCWK_TEMP1, @SCWK_ANSWER)
    _ADD_ITEM(20, @SCWK_TEMP1, @SCWK_ANSWER)
"""

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.ev"
            path.write_text(source, encoding="utf-8")
            matches = scan_file(path)

        self.assertEqual(
            matches,
            [("ev_sample", 2, [], 20, 5)],
        )

    def test_write_item_map_merges_resolved_entries_without_duplicates(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            item_map_path = Path(temporary_directory) / "item_map.json"
            item_map_path.write_text(
                json.dumps(
                    {
                        "door": [
                            {
                                "id": 216,
                                "quantity": 1,
                                "label_name": "existing_label",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            write_item_map(
                item_map_path,
                [
                    (
                        Path("sample.ev"),
                        "ev_sample",
                        2,
                        [],
                        20,
                        5,
                    ),
                    (
                        Path("sample.ev"),
                        "ev_sample",
                        2,
                        [],
                        20,
                        5,
                    ),
                    (
                        Path("sample.ev"),
                        "ev_unresolved",
                        3,
                        [],
                        None,
                        None,
                    ),
                ],
            )

            item_map = json.loads(item_map_path.read_text(encoding="utf-8"))

        self.assertEqual(
            item_map["sample"],
            [
                {
                    "id": 20,
                    "quantity": 5,
                    "label_name": "ev_sample",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
