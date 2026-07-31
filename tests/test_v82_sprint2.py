import unittest
from pathlib import Path
from modules.patch_planner import PatchPlanner
from modules.patch_preview import PatchPreview

class TestV82Sprint2(unittest.TestCase):
    def setUp(self):
        self.planner = PatchPlanner()
        self.preview = PatchPreview()
        self.test_file = Path("data/dummy_preview_target.py")
        self.test_file.write_text("try:\n    val = 42\nexcept:\n    pass  \n", encoding="utf-8")

    def test_patch_planner_and_preview(self):
        # 1. Generate plan
        plan = self.planner.generate_plan(str(self.test_file))
        self.assertTrue(plan["success"])
        self.assertEqual(plan["risk"], "LOW")
        self.assertGreater(plan["changes_applied"], 0)
        self.assertIn("Replace bare except", plan["change_items"][0])

        # 2. Render diff preview
        diff_output = self.preview.render_diff(
            plan["file"],
            plan["original_code"],
            plan["transformed_code"]
        )
        self.assertIn("Previewing Patch for:", diff_output)
        self.assertIn("[Old] except:", diff_output)
        self.assertIn("[New] except Exception:", diff_output)

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

if __name__ == "__main__":
    unittest.main()