# modules/rollback.py
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

class RollbackEngine:
    def __init__(self, backup_dir: str = "data/.backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, patch_id: str, file_paths: List[str]) -> Path:
        """Copies target files into a isolated backup staging directory."""
        snapshot_path = self.backup_dir / patch_id
        snapshot_path.mkdir(parents=True, exist_ok=True)

        for file_path in file_paths:
            src = Path(file_path)
            if src.exists():
                dest = snapshot_path / src.name
                shutil.copy2(src, dest)
        
        return snapshot_path

    def restore_snapshot(self, patch_id: str, file_paths: List[str]) -> bool:
        """Restores original files from snapshot if patch fails validation."""
        snapshot_path = self.backup_dir / patch_id
        if not snapshot_path.exists():
            return False

        for file_path in file_paths:
            target = Path(file_path)
            backup = snapshot_path / target.name
            if backup.exists():
                shutil.copy2(backup, target)
        
        self.cleanup_snapshot(patch_id)
        return True

    def cleanup_snapshot(self, patch_id: str) -> None:
        """Removes the temporary staging backup after successful verification."""
        snapshot_path = self.backup_dir / patch_id
        if snapshot_path.exists():
            shutil.rmtree(snapshot_path)