import importlib
import os
import sys
from modules.logger import log_info, log_error

SKILLS_DIR = "skills"
_registry = {}

def load_skills():
    """
    Nova v46 Dynamic Plugin Loader.
    Sweeps the skills/ directory and loads self-registering scripts automatically.
    """
    global _registry
    _registry.clear()
    
    if not os.path.exists(SKILLS_DIR):
        os.makedirs(SKILLS_DIR, exist_ok=True)
        log_info("PluginEngine", "Created empty skills/ directory.")
        return _registry

    # Add skills folder to the system path so Python can find the files inside
    if os.path.abspath(SKILLS_DIR) not in sys.path:
        sys.path.append(os.path.abspath(SKILLS_DIR))

    for filename in os.listdir(SKILLS_DIR):
        if filename.endswith(".py") and not filename.startswith("__"):
            skill_name = filename[:-3]
            try:
                # Dynamic import compilation step
                module = importlib.import_module(skill_name)
                
                # Check if the module follows the official Nova v46 Skill Specification Blueprint
                if hasattr(module, "SKILL_MANIFEST") and hasattr(module, "execute"):
                    manifest = module.SKILL_MANIFEST
                    intent_trigger = manifest.get("intent_trigger")
                    
                    if intent_trigger:
                        _registry[intent_trigger] = {
                            "module": module,
                            "description": manifest.get("description", ""),
                            "parameter_key": manifest.get("parameter_key")
                        }
                        log_info("PluginEngine", f"Successfully registered skill plugin: {skill_name} on trigger [{intent_trigger}]")
                else:
                    log_error("PluginEngine", f"Skipped file '{filename}': Missing manifest specification structures.")
            except Exception as e:
                log_error("PluginEngine", f"Failed to mount skill plugin '{filename}': {e}")
                
    return _registry

def get_plugin_routes():
    """Returns the live memory map of all successfully bound dynamic skill handlers."""
    return _registry