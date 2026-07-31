import json
import os
from typing import Dict, List, Optional

class DecisionEngine:
    def __init__(self, data_path: str = 'data/decisions.json'):
        self.data_path = data_path
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        if not os.path.exists(self.data_path):
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({"decisions": []}, f, indent=2)

    def load_decisions(self) -> List[Dict]:
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f).get("decisions", [])
        except Exception:
            return []

    def save_decisions(self, decisions: List[Dict]):
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump({"decisions": decisions}, f, indent=2)

    def create_decision(self, title: str, decision: str, reason: str, tradeoffs: str, status: str = "Accepted") -> Dict:
        decisions = self.load_decisions()
        adr_id = f"ADR-{len(decisions) + 1:03d}"
        new_adr = {
            "id": adr_id,
            "title": title,
            "decision": decision,
            "reason": reason,
            "tradeoffs": tradeoffs,
            "status": status
        }
        decisions.append(new_adr)
        self.save_decisions(decisions)
        return new_adr

    def get_decision(self, adr_id: str) -> Optional[Dict]:
        for d in self.load_decisions():
            if d.get("id").upper() == adr_id.upper():
                return d
        return None

    def format_list(self) -> str:
        decisions = self.load_decisions()
        if not decisions:
            return "No Architecture Decision Records (ADRs) logged yet."
        out = ["\n==================================================",
               "       ARCHITECTURE DECISION RECORDS (ADR)        ",
               "=================================================="]
        for d in decisions:
            out.append(f"[{d['id']}] {d['title']} | Status: {d['status']}")
            out.append(f"   Decision: {d['decision']}")
            out.append("--------------------------------------------------")
        return "\n".join(out)

    def format_adr(self, adr_id: str) -> str:
        adr = self.get_decision(adr_id)
        if not adr:
            return f"WARNING: {adr_id} not found."
        return (
            f"\n{adr['id']}: {adr['title']}\n\n"
            f"Decision:\n  {adr['decision']}\n\n"
            f"Reason:\n  {adr['reason']}\n\n"
            f"Tradeoffs:\n  {adr['tradeoffs']}\n\n"
            f"Status:\n  {adr['status']}\n"
        )
