import os
from modules.logger import log_info, log_error

class WorkspaceSentry:
    """Monitors and profiles the active operating directory and project roots."""
    def __init__(self):
        self.current_dir = os.getcwd()
        self.project_root = self._detect_project_root()

    def update_cwd(self, path: str) -> bool:
        """Changes the tracking directory and updates the project root context."""
        try:
            target_path = os.path.abspath(path)
            if os.path.isdir(target_path):
                os.chdir(target_path)
                self.current_dir = target_path
                self.project_root = self._detect_project_root()
                log_info("WorkspaceSentry", f"Directory pivoted to: {self.current_dir}")
                return True
            return False
        except Exception as e:
            log_error("WorkspaceSentry", f"Failed to change directory: {e}")
            return False

    def _detect_project_root(self) -> str:
        """Traverses upwards from the current folder to identify a project anchor."""
        anchors = {".git", "requirements.txt", "package.json", "setup.py", "main.py"}
        current = os.path.abspath(self.current_dir)
        
        while True:
            # Check if any root anchors exist in the current folder level
            if any(os.path.exists(os.path.join(current, anchor)) for anchor in anchors):
                return current
            
            # Stop if we hit the file system root
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
            
        return self.current_dir  # Fallback to CWD if no root anchor is found

    def inspect_workspace(self) -> dict:
        """Profiles the active directory to gather telemetry on its structural footprint."""
        metrics = {
            "cwd": self.current_dir,
            "project_root": self.project_root,
            "total_files": 0,
            "languages": set()
        }
        
        try:
            for root, dirs, files in os.walk(self.current_dir):
                # Avoid crawling deep dependency directories
                dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", "venv"}]
                metrics["total_files"] += len(files)
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext:
                        metrics["languages"].add(ext)
        except Exception as e:
            log_error("WorkspaceSentry", f"Error profiling workspace: {e}")
            
        return metrics

# Global active workspace tracker
active_workspace = WorkspaceSentry()