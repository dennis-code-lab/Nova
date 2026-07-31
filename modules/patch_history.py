# modules/patch_history.py
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class PatchHistory:
    def __init__(self, history_file: str = "data/patch_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.history_file.exists():
            self._save({"patches": []})

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"patches": []}

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def log_patch(
        self,
        patch_id: str,
        files_changed: List[str],
        reason: str,
        health_before: float,
        health_after: float,
        test_status: str = "PASS"
    ) -> Dict[str, Any]:
        """Appends a completed patch run to the history ledger."""
        data = self._load()
        entry = {
            "patch_id": patch_id,
            "timestamp": datetime.now().isoformat(),
            "files_changed": files_changed,
            "reason": reason,
            "health_before": health_before,
            "health_after": health_after,
            "test_status": test_status
        }
        data["patches"].append(entry)
        self._save(data)
        return entry

    def get_history(self) -> List[Dict[str, Any]]:
        return self._load().get("patches", [])