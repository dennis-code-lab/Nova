"""
Nova Engine v98
Engineering History

Tracks completed engineering improvements using
persistent Engineering Memory.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_memory import EngineeringMemory


@dataclass
class EngineeringHistory:

    memory: EngineeringMemory

    def complete(self, module: str) -> None:
        """Marks a given module as completed in persistent storage."""
        self.memory.complete_module(module)

    def is_completed(self, module: str) -> bool:
        """Checks if a module is marked as completed."""
        return self.memory.is_completed(module)

    def completed_count(self) -> int:
        """Returns the total number of completed modules."""
        return len(self.memory.completed_modules())

    def completed_modules(self) -> list[str]:
        """Returns all completed modules."""
        return self.memory.completed_modules()

    def remaining(self, modules: list[str]) -> list[str]:
        """Returns a list of module names that have not yet been completed."""
        completed = set(self.memory.completed_modules())
        return [module for module in modules if module not in completed]