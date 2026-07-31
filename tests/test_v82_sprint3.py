import unittest
import shutil
from pathlib import Path
from modules.engineering_controller import EngineeringController

class TestV82Sprint3(unittest.TestCase):
    def setUp(self):
        self.controller = EngineeringController()
        self.dummy_file = Path("modules/dummy_calc.py")
        self.dummy_file.write_text("def add(a, b):\n    try:\n        return a + b\n    except:\n        return None   \n", encoding="utf-8")

    def test_improve_target_flow_with_auto_approve(self):
        # Test full refactor -> test -> pass pipeline with auto-approval
        res = self.controller.improve_target(str(self.dummy_file), auto_approve=True)
        self.assertTrue(res["success"])
        self.assertTrue(res["applied"])

        # Check transformed code
        updated_code = self.dummy_file.read_text(encoding="utf-8")
        self.assertIn("except Exception:", updated_code)

    def tearDown(self):
        if self.dummy_file.exists():
            self.dummy_file.unlink()

if __name__ == "__main__":
    unittest.main()