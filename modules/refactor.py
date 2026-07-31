import os
import ast
import re
from typing import List, Dict, Any, Set

class RefactorEngine:
    """
    RefactorEngine analyzes Python source code AST to detect code-quality issues,
    bad smells, and anti-patterns.
    
    It integrates directly with the output of CodeIntelEngine (AST representations).
    """
    
    def __init__(self, max_method_lines: int = 60, max_params: int = 5, max_nesting: int = 4, max_class_methods: int = 20):
        self.max_method_lines = max_method_lines
        self.max_params = max_params
        self.max_nesting = max_nesting
        self.max_class_methods = max_class_methods
        
        # Simple heuristic pattern for low-effort or uninformative variable names
        self.bad_variable_pattern = re.compile(r'^(?:[xyzabc]|tmp|temp|data\d*|val\d*|obj|var|foo|bar|baz|abcdata\d*)$', re.IGNORECASE)

    def analyze_source(self, source_code: str, filename: str = "<string>") -> List[Dict[str, Any]]:
        """Parses source code into an AST and runs full analysis."""
        try:
            tree = ast.parse(source_code, filename=filename)
            return self.analyze_ast(tree, source_code)
        except SyntaxError as e:
            return [{
                "type": "SyntaxError",
                "line": e.lineno,
                "message": f"Failed to parse AST: {e.msg}",
                "severity": "CRITICAL"
            }]

    def analyze_ast(self, tree: ast.AST, raw_source: str) -> List[Dict[str, Any]]:
        """
        Analyzes an existing AST. If raw_source is provided, it helps calculate
        exact lines of code for complex multi-line constructs.
        """
        findings = []
        lines = raw_source.splitlines() if raw_source else []
        
        # Extract duplicate/unused import trackers
        imported_names: Dict[str, List[Dict[str, Any]]] = {} # name -> list of import occurrences
        used_names: Set[str] = set()
        
        # Traverse tree for general node inspection
        for node in ast.walk(tree):
            # Track Name references to detect unused imports
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Also capture the base object of an attribute (e.g., 'os' in 'os.path')
                curr = node.value
                while isinstance(curr, ast.Attribute):
                    curr = curr.value
                if isinstance(curr, ast.Name):
                    used_names.add(curr.id)
            
            # 1. Imports Collection (Detect Duplicates)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._collect_imports(node, imported_names)
            
            # 2. Large Classes Detector
            if isinstance(node, ast.ClassDef):
                self._check_large_class(node, findings)
                
            # 3. Function & Method Level Checks (Length, Params, Nesting)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check_function_signatures(node, findings)
                self._check_method_length(node, lines, findings)
                self._check_nesting_depth(node, findings)
                self._check_variable_names(node, findings)
                
        # 4. Process collected imports for duplicate and unused findings
        self._analyze_imports(imported_names, used_names, findings)
        
        # Sort findings by line number
        findings.sort(key=lambda x: x.get("line", 0))
        return findings

    def _collect_imports(self, node: Any, imported_names: Dict[str, List[Dict[str, Any]]]):
        """Tracks where and how modules are imported."""
        line_no = getattr(node, 'lineno', 0)
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.setdefault(name, []).append({"name": alias.name, "line": line_no, "node": node})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                name = alias.asname or alias.name
                full_import_path = f"{module}.{alias.name}" if module else alias.name
                imported_names.setdefault(name, []).append({"name": full_import_path, "line": line_no, "node": node})

    def _analyze_imports(self, imported_names: Dict[str, List[Dict[str, Any]]], used_names: Set[str], findings: List[Dict[str, Any]]):
        """Identifies duplicate imports and unused imports."""
        for local_name, occurrences in imported_names.items():
            # Check Duplicates
            if len(occurrences) > 1:
                lines = [occ["line"] for occ in occurrences]
                findings.append({
                    "type": "DuplicateImport",
                    "line": occurrences[-1]["line"],
                    "message": f"Duplicate import detected: '{local_name}' is imported multiple times (lines {', '.join(map(str, lines))}).",
                    "severity": "WARNING"
                })
            
            # Check Unused (exclude standard dunder references and self/cls lookups)
            # Safe guards to ensure we don't flag module names if referenced
            base_module_name = local_name.split('.')[0]
            if base_module_name not in used_names and local_name not in used_names:
                # Avoid flagging common conventions if they are module wrappers
                findings.append({
                    "type": "UnusedImport",
                    "line": occurrences[0]["line"],
                    "message": f"Unused import: '{local_name}' is imported but never referenced in the scope.",
                    "severity": "WARNING"
                })

    def _check_large_class(self, node: ast.ClassDef, findings: List[Dict[str, Any]]):
        """Flags classes containing too many methods."""
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if len(methods) > self.max_class_methods:
            findings.append({
                "type": "LargeClass",
                "line": node.lineno,
                "message": f"Class '{node.name}' has too many methods ({len(methods)} > max {self.max_class_methods}).",
                "severity": "WARNING"
            })

    def _check_function_signatures(self, node: Any, findings: List[Dict[str, Any]]):
        """Flags parameters exceeding safe thresholds."""
        # Calculate total positional, keyword, and varargs parameters
        total_args = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            total_args += 1
        if node.args.kwarg:
            total_args += 1
            
        if total_args > self.max_params:
            findings.append({
                "type": "TooManyParameters",
                "line": node.lineno,
                "message": f"Function '{node.name}' has {total_args} parameters (threshold is {self.max_params}).",
                "severity": "WARNING"
            })

    def _check_method_length(self, node: Any, lines: List[str], findings: List[Dict[str, Any]]):
        """Calculates physical lines of a method/function block."""
        if not hasattr(node, 'end_lineno') or not lines:
            return
        
        start = node.lineno
        end = node.end_lineno
        physical_lines = lines[start-1:end]
        
        # Filter out comments and blank lines for logical count
        logical_lines_count = 0
        for line in physical_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                logical_lines_count += 1
                
        if logical_lines_count > self.max_method_lines:
            findings.append({
                "type": "LongMethod",
                "line": start,
                "message": f"Function '{node.name}' is too long ({logical_lines_count} logical lines > max {self.max_method_lines}).",
                "severity": "WARNING"
            })

    def _check_nesting_depth(self, node: Any, findings: List[Dict[str, Any]]):
        """Measures control flow nesting levels inside a function."""
        max_seen_depth = 0
        
        # Target control structures that add nesting overhead
        nesting_nodes = (ast.If, ast.While, ast.For, ast.Try, ast.With, ast.AsyncFor, ast.AsyncWith)
        
        # Track active block depth traversal mapping
        def walk_depth(inner_node: ast.AST, current_depth: int):
            nonlocal max_seen_depth
            if isinstance(inner_node, nesting_nodes):
                current_depth += 1
                if current_depth > max_seen_depth:
                    max_seen_depth = current_depth
            
            for child in ast.iter_child_nodes(inner_node):
                walk_depth(child, current_depth)

        # Walk children of the function body
        for child in node.body:
            walk_depth(child, current_depth=0)
            
        if max_seen_depth > self.max_nesting:
            findings.append({
                "type": "DeepNesting",
                "line": node.lineno,
                "message": f"Function '{node.name}' exceeds maximum control nesting ({max_seen_depth} levels > allowed {self.max_nesting}).",
                "severity": "WARNING"
            })

    def _check_variable_names(self, node: Any, findings: List[Dict[str, Any]]):
        """Scours assignments inside functions for non-descriptive names."""
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    # Check plain variables
                    if isinstance(target, ast.Name):
                        self._validate_var_name(target.id, target.lineno, node.name, findings)
                    # Check unpack assignments: a, b = c
                    elif isinstance(target, (ast.Tuple, ast.List)):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                self._validate_var_name(elt.id, elt.lineno, node.name, findings)

    def _validate_var_name(self, var_name: str, line_no: int, func_name: str, findings: List[Dict[str, Any]]):
        if self.bad_variable_pattern.match(var_name):
            findings.append({
                "type": "BadVariableName",
                "line": line_no,
                "message": f"Non-descriptive variable name '{var_name}' found in function '{func_name}'.",
                "severity": "INFO"
            })

    def audit_workspace(self, root_dir: str) -> List[Dict[str, Any]]:
        """
        v79 Capability: Scans all accessible Python files inside the workspace root.
        Generates and injects session tracking identifiers for interactive management.
        """
        workspace_findings = []
        global_issue_counter = 1

        for root, _, files in os.walk(root_dir):
            # Ignore development setups and virtual environment overhead paths
            if any(part in root for part in [".git", "venv", "__pycache__", "env", ".pytest_cache"]):
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            source = f.read()
                        
                        # Generate core AST structures
                        tree = ast.parse(source, filename=file_path)
                        file_findings = self.analyze_ast(tree, source)

                        # Enforce tracking data fields onto active dictionaries
                        for finding in file_findings:
                            finding["id"] = f"REF-{global_issue_counter}"
                            finding["file"] = rel_path.replace("\\", "/") # Unified platform forward slashes
                            finding["suppressed"] = False
                            workspace_findings.append(finding)
                            global_issue_counter += 1
                    except Exception:
                        # Gracefully skip parsing errors for corrupt/incomplete script modules
                        continue

        return workspace_findings

# Global Single Instance Initialization export
refactor_engine = RefactorEngine()