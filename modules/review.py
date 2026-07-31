import os
import ast

class CodeReviewer:
    """
    Nova v79 Core Module: Intelligent Code Review Assistant.
    Parses workspace code structures to audit security, style guidelines, 
    and session-level optimization metrics.
    """
    def __init__(self):
        # Extended configurations: ease up the line length threshold to modern standards
        self.max_line_length = 120  # Modern standard boundary (prevents line noise)
        
    def audit_workspace(self, workspace_root):
        """
        Scans all Python files across the active project root directory.
        Returns a structured schema mapping telemetry data and flagged violations.
        """
        report = {
            "meta": {
                "files_checked": 0,
                "timestamp": None
            },
            "violations": []
        }
        
        if not os.path.exists(workspace_root):
            return report

        for root, _, files in os.walk(workspace_root):
            # Skip hidden folders or virtual environments to avoid noise
            if any(part.startswith('.') or part in ['venv', '__pycache__', 'env'] for part in root.split(os.sep)):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, workspace_root)
                    report["meta"]["files_checked"] += 1
                    
                    # Run static checks on the target file
                    self._check_file_contents(file_path, relative_path, report["violations"])
                    
        return report

    def _check_file_contents(self, file_path, relative_path, violations_list):
        """Performs structural AST parsing and raw analysis on a single target script."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                lines = source.splitlines()
        except Exception:
            return # Skip files that cannot be processed due to encoding mismatches

        # 1. Raw Line-by-Line Static Scans (PEP 8 Style Rules)
        for idx, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                violations_list.append({
                    "file": relative_path,
                    "line": idx,
                    "category": "style",
                    "summary": f"Line exceeds maximum PEP 8 target width limit ({len(line)} > {self.max_line_length} chars)"
                })

        # 2. Structural Code Smells & Security Intercepts via AST Analysis
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                # Intercept dangerous evaluations (Security Risk)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    violations_list.append({
                        "file": relative_path,
                        "line": node.lineno,
                        "category": "security",
                        "summary": "Use of raw 'eval()' detected. Secure alternative parsers or strict filtering required."
                    })
                
                # Check for bare exception handling blocks (Anti-Pattern / Style Risk)
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    violations_list.append({
                        "file": relative_path,
                        "line": node.lineno,
                        "category": "optimization",
                        "summary": "Bare 'except:' handler catch-all detected. Switch to specific exception classes."
                    })
        except SyntaxError:
            # Drop a warning pin if the file has corrupted syntax structures
            violations_list.append({
                "file": relative_path,
                "line": 1,
                "category": "critical",
                "summary": "AST Compilation Error: Source file contains broken Python syntax."
            })