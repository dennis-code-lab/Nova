import unittest
import shutil
from pathlib import Path
from modules.rollback import RollbackEngine
from modules.patch_history import PatchHistory
from modules.refactor_engine import RefactorEngine

class TestV82Sprint1(unittest.TestCase):
    def setUp(self):
        self.backup_dir = Path("data/.test_backups")
        self.history_file = Path("data/test_patch_history.json")
        self.rollback = RollbackEngine(backup_dir=str(self.backup_dir))
        self.history = PatchHistory(history_file=str(self.history_file))
        self.refactor = RefactorEngine()

    def test_refactor_and_rollback_flow(self):
        # 1. Create a temporary test target file with code issues
        test_file = Path("data/dummy_target.py")
        test_file.write_text("try:\n    x = 1\nexcept:\n    pass   \n", encoding="utf-8")

        # 2. Create snapshot backup
        self.rollback.create_snapshot("PATCH_001", [str(test_file)])

        # 3. Refactor in memory
        res = self.refactor.refactor_file(str(test_file))
        self.assertTrue(res["success"])
        self.assertIn("except Exception:", res["transformed_code"])

        # Write modified code to disk
        test_file.write_text(res["transformed_code"], encoding="utf-8")

        # 4. Log patch to audit ledger
        entry = self.history.log_patch(
            patch_id="PATCH_001",
            files_changed=[str(test_file)],
            reason="Fix bare except and whitespace",
            health_before=85.0,
            health_after=86.4,
            test_status="PASS"
        )
        self.assertEqual(entry["patch_id"], "PATCH_001")

        # 5. Restore original file (Rollback)
        self.rollback.restore_snapshot("PATCH_001", [str(test_file)])
        restored_text = test_file.read_text(encoding="utf-8")
        
        # Verify it reverted back to bare 'except:'
        self.assertIn("except:", restored_text)

        # Cleanup test artifacts
        if test_file.exists(): 
            test_file.unlink()

    def tearDown(self):
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        if self.history_file.exists():
            self.history_file.unlink()

if __name__ == "__main__":
    unittest.main()