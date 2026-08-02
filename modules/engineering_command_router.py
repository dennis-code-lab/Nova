"""
Nova Engine v91
Engineering Command Router

Central router for all Engineering Intelligence commands.
"""

from __future__ import annotations

from typing import Any, Optional

from modules.engineering_runtime import EngineeringRuntime


class EngineeringCommandRouter:

    def __init__(self, runtime: EngineeringRuntime) -> None:
        self.runtime = runtime

    def execute(self, command: str) -> Optional[Any]:
        lower = command.lower().strip()

        if lower == "engineering dashboard":
            return self.runtime.dashboard()

        if lower == "engineering progress":
            return self.runtime.progress()

        if lower == "engineering roadmap":
            return self.runtime.roadmap()

        if lower == "engineering overview":
            return self.runtime.overview()

        if lower == "engineering forecast":
            return self.runtime.forecast()

        if lower == "engineering decision":
            return self.runtime.decision()

        if lower.startswith("engineering simulate "):
            module = command[len("engineering simulate ") :].strip()
            return self.runtime.simulate(module)

        if lower.startswith("engineering report "):
            module = command[len("engineering report ") :].strip()
            return self.runtime.report(module)

        if lower.startswith("engineering plan "):
            module = command[len("engineering plan ") :].strip()
            return self.runtime.plan(module)

        if lower.startswith("engineering predict "):
            module = command[len("engineering predict ") :].strip()
            return self.runtime.predict(module)

        if lower.startswith("engineering risk "):
            module = command[len("engineering risk ") :].strip()
            return self.runtime.risk(module)

        if lower.startswith("engineering explain "):
            module = command[len("engineering explain ") :].strip()
            return self.runtime.explain(module)

        if lower.startswith("engineering advise "):
            module = command[len("engineering advise ") :].strip()
            return self.runtime.advise(module)

        if lower.startswith("engineering complete "):
            module = command[len("engineering complete ") :].strip()
            self.runtime.complete(module)
            return f"Marked '{module}' as completed."

        return None