# modules/refactor_engine.py
import re
import ast
from pathlib import Path
from typing import Dict, Any, Tuple

class RefactorEngine:
    def __init__(self):
        pass

    def replace_bare_except(self, code: str) -> Tuple[str, int]:
        """Replaces bare 'except:' with 'except Exception:' using AST verification."""
        # Regex replacement targeting bare excepts while preserving indentation
        pattern = r"(\bexcept\s*):"
        replacement = r"\1 Exception:"
        
        new_code, count = re.subn(pattern, replacement, code)
        
        # Verify syntax remains valid Python AST
        if count > 0:
            try:
                ast.parse(new_code)
            except SyntaxError:
                # Fallback if transformation broke AST syntax
                return code, 0
                
        return new_code, count

    def normalize_whitespace(self, code: str) -> Tuple[str, int]:
        """Removes trailing whitespace on each line and trailing blank lines."""
        lines = code.splitlines()
        modified_count = 0
        cleaned_lines = []

        for line in lines:
            stripped = line.rstrip()
            if stripped != line:
                modified_count += 1
            cleaned_lines.append(stripped)

        result_code = "\n".join(cleaned_lines) + "\n"
        return result_code, modified_count

    def refactor_file(self, file_path: str) -> Dict[str, Any]:
        """Applies all safe transformations to target file in memory."""
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "reason": f"File {file_path} not found"}

        with open(path, "r", encoding="utf-8") as f:
            original_code = f.read()

        code_after_except, except_fixes = self.replace_bare_except(original_code)
        final_code, whitespace_fixes = self.normalize_whitespace(code_after_except)

        total_changes = except_fixes + whitespace_fixes
        
        return {
            "success": True,
            "file": file_path,
            "original_code": original_code,
            "transformed_code": final_code,
            "changes_applied": total_changes,
            "summary": {
                "bare_except_fixes": except_fixes,
                "whitespace_fixes": whitespace_fixes
            }
        }