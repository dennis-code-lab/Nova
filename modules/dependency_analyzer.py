"""
Nova Engine v84
Dependency Intelligence Layer

dependency_analyzer.py

Purpose:
    Analyze Python source files and build a dependency graph
    using the Python Abstract Syntax Tree (AST).

Author:
    Nova Engine
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Union


# ==========================================================
# Data Models
# ==========================================================

@dataclass
class DependencyGraph:
    """
    Represents module dependency relationships.
    """

    graph: Dict[str, Set[str]] = field(default_factory=dict)

    def add_module(self, module: str) -> None:
        """
        Ensure a module exists even if it has no imports.
        """
        self.graph.setdefault(module, set())

    def add_dependency(self, module: str, dependency: str) -> None:
        """
        Register a dependency.
        """
        self.add_module(module)
        self.graph[module].add(dependency)

    def dependencies_of(self, module: str) -> Set[str]:
        return self.graph.get(module, set())

    def modules(self) -> List[str]:
        return sorted(self.graph.keys())

    def total_modules(self) -> int:
        return len(self.graph)

    def total_edges(self) -> int:
        return sum(len(v) for v in self.graph.values())


# ==========================================================
# Dependency Analyzer
# ==========================================================

class DependencyAnalyzer:
    """
    Builds dependency relationships between Python files.
    """

    def __init__(self, workspace: Union[str, Path]) -> None:
        self.workspace = Path(workspace)
        self.graph = DependencyGraph()

    # ------------------------------------------------------

    def analyze(self) -> DependencyGraph:
        """
        Analyze every Python file in the workspace.
        """
        for file in self.workspace.rglob("*.py"):
            self._analyze_file(file)

        return self.graph

    # ------------------------------------------------------

    def _analyze_file(self, file_path: Path) -> None:
        """
        Parse one Python file.
        """
        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception:
            return

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return

        module_name = self._module_name(file_path)

        # Every Python file should appear in the graph,
        # even if it imports nothing.
        self.graph.add_module(module_name)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.graph.add_dependency(
                        module_name,
                        alias.name,
                    )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.graph.add_dependency(
                        module_name,
                        node.module,
                    )

    # ------------------------------------------------------

    def _module_name(self, file_path: Path) -> str:
        """
        Convert file path into module notation.

        Example:
            modules/memory.py -> modules.memory
        """
        relative = file_path.relative_to(self.workspace)
        return ".".join(relative.with_suffix("").parts)


# ==========================================================
# Standalone Demo
# ==========================================================

if __name__ == "__main__":

    analyzer = DependencyAnalyzer(".")
    graph = analyzer.analyze()

    print("=" * 50)
    print("Dependency Graph")
    print("=" * 50)

    for module_item in graph.modules():
        print(f"\n{module_item}")

        for dep in sorted(graph.dependencies_of(module_item)):
            print(f"    -> {dep}")

    print("\nSummary")
    print("-" * 50)
    print(f"Modules      : {graph.total_modules()}")
    print(f"Dependencies : {graph.total_edges()}")