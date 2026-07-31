# modules/code_intel.py
import ast
import os
from modules.logger import log_info, log_error

class CodeIntelEngine:
    """Uses Abstract Syntax Trees (AST) to map, parse, and analyze Python source structures."""
    
    def parse_file_structure(self, file_path: str, return_raw: bool = False) -> dict:
        """Parses a Python file and returns its classes, methods, and stand-alone functions."""
        if not os.path.exists(file_path):
            log_error("CodeIntel", f"Target file not found for parsing: {file_path}")
            return {"error": "File not found"}
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
                
            tree = ast.parse(source, filename=file_path)
            
            structure = {
                "classes": {},
                "functions": [],
                "imports": []
            }
            
            for node in ast.iter_child_nodes(tree):
                # Parse Global Imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            structure["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            structure["imports"].append(f"{module}.{alias.name}")
                
                # Parse Top-level Functions
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [arg.arg for arg in node.args.args]
                    structure["functions"].append({
                        "name": node.name,
                        "args": args,
                        "line": node.lineno,
                        "async": isinstance(node, ast.AsyncFunctionDef)
                    })
                    
                # Parse Classes
                elif isinstance(node, ast.ClassDef):
                    class_data = {
                        "methods": [],
                        "line": node.lineno,
                        "bases": [ast.unparse(b) for b in node.bases] if hasattr(ast, "unparse") else []
                    }
                    for subnode in node.body:
                        if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            sub_args = [arg.arg for arg in subnode.args.args]
                            class_data["methods"].append({
                                "name": subnode.name,
                                "args": sub_args,
                                "line": subnode.lineno,
                                "async": isinstance(subnode, ast.AsyncFunctionDef)
                            })
                    structure["classes"][node.name] = class_data
            
            if return_raw:
                return {
                    "structure": structure,
                    "tree": tree,
                    "source": source
                }
            return structure
            
        except Exception as e:
            log_error("CodeIntel", f"AST parsing failure on {file_path}: {e}")
            return {"error": str(e)}

    def locate_declaration(self, workspace_root: str, target_name: str) -> list:
        """Searches across the workspace to locate where a class or function is declared."""
        matches = []
        for root, _, files in os.walk(workspace_root):
            if any(p in root for p in [".git", "venv", "__pycache__", "node_modules"]):
                continue
                
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    structure = self.parse_file_structure(full_path)
                    
                    if "error" in structure:
                        continue
                        
                    # Check top-level functions
                    for func in structure["functions"]:
                        if func["name"] == target_name:
                            matches.append({
                                "type": "Function",
                                "name": target_name,
                                "file": os.path.relpath(full_path, workspace_root),
                                "line": func["line"]
                            })
                            
                    # Check Classes and Methods
                    for class_name, class_info in structure["classes"].items():
                        if class_name == target_name:
                            matches.append({
                                "type": "Class",
                                "name": target_name,
                                "file": os.path.relpath(full_path, workspace_root),
                                "line": class_info["line"]
                            })
                        for method in class_info["methods"]:
                            if method["name"] == target_name:
                                matches.append({
                                    "type": f"Method (Class: {class_name})",
                                    "name": target_name,
                                    "file": os.path.relpath(full_path, workspace_root),
                                    "line": method["line"]
                                })
                                
        return matches

# Global instance of local Code Intelligence Engine
code_intel = CodeIntelEngine()