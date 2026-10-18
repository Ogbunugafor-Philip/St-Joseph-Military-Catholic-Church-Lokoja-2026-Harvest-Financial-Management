import ast
import unittest
from pathlib import Path


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("app.py").read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_completed_pages_are_reachable_from_navigation(self):
        self.assertIn('"Downloads / View Data"', self.source)
        self.assertIn('"Admin Dashboard"', self.source)

    def test_admin_pages_retain_authentication_gate(self):
        for page in ("Admin Dashboard", "Admin Editor (Edit/Delete)"):
            marker = f'elif page == "{page}":'
            section = self.source.split(marker, 1)[1].split("elif page ==", 1)[0]
            self.assertIn("require_admin_login()", section)


if __name__ == "__main__":
    unittest.main()
