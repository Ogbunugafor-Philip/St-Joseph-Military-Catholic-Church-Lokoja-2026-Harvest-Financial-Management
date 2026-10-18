import io
import unittest

import pandas as pd

from export_safety import safe_csv_bytes, spreadsheet_safe_text


class ExportSafetyTests(unittest.TestCase):
    def test_formula_prefixes_are_escaped(self):
        for prefix in ("=", "+", "-", "@", "\t", "\r", "\n"):
            with self.subTest(prefix=repr(prefix)):
                self.assertTrue(spreadsheet_safe_text(prefix + "payload").startswith("'"))

    def test_normal_text_and_numbers_are_preserved(self):
        self.assertEqual(spreadsheet_safe_text("Synthetic Person"), "Synthetic Person")
        self.assertEqual(spreadsheet_safe_text(500), 500)

    def test_csv_escapes_formula_cells(self):
        payload = safe_csv_bytes(pd.DataFrame({"Name": ["=1+1"], "Amount": [500]}))
        frame = pd.read_csv(io.BytesIO(payload))
        self.assertEqual(frame.loc[0, "Name"], "'=1+1")
        self.assertEqual(frame.loc[0, "Amount"], 500)


if __name__ == "__main__":
    unittest.main()
