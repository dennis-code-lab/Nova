# modules/patch_planner.py
import uuid
from pathlib import Path
from typing import Dict, Any, List
from modules.refactor_engine import RefactorEngine

class PatchPlanner:
    def __init__(self):
        self.refactor_engine = RefactorEngine()

    def generate_plan(self, file_path: str) -> Dict[str, Any]:
        """Inspects target file and creates an actionable patch plan."""
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "reason": f"File '{file_path}' does not exist."
            }

        refactor_result = self.refactor_engine.refactor_file(file_path)
        if not refactor_result["success"]:
            return refactor_result

        changes_applied = refactor_result["changes_applied"]
        summary = refactor_result["summary"]

        # Calculate proposed changes list
        change_items = []
        if summary.get("bare_except_fixes", 0) > 0:
            change_items.append(f"Replace bare except ({summary['bare_except_fixes']} occurrence(s))")
        if summary.get("whitespace_fixes", 0) > 0:
            change_items.append(f"Normalize trailing whitespace ({summary['whitespace_fixes']} line(s))")

        # Estimate health gain and risk assessment
        health_gain = round(changes_applied * 0.4, 1) if changes_applied > 0 else 0.0
        risk = "LOW" if changes_applied < 10 else "MEDIUM"

        patch_id = f"PATCH_{uuid.uuid4().hex[:6].upper()}"

        return {
            "success": True,
            "patch_id": patch_id,
            "file": file_path,
            "changes_applied": changes_applied,
            "change_items": change_items,
            "risk": risk,
            "estimated_health_gain": health_gain,
            "original_code": refactor_result["original_code"],
            "transformed_code": refactor_result["transformed_code"]
        }