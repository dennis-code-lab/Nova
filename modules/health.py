import os
import sys
import threading
from modules.logger import log_info, log_error
from modules import settings

SYSTEM_CRITICAL_FILES = [
    "data/memory.json",
    "data/plugin_config.json",
    "modules/help_system.py"
]

def audit_file_integrity() -> tuple:
    """Checks for missing core files and restores defaults to prevent crashes."""
    issues_found = []
    restored_files = []
    
    for filepath in SYSTEM_CRITICAL_FILES:
        if not os.path.exists(filepath):
            issues_found.append(f"Missing: {filepath}")
            # Run specific recovery routines based on the file type
            if filepath == "data/plugin_config.json":
                settings.initialize_settings()
                restored_files.append(filepath)
            elif filepath == "data/memory.json":
                from modules.memory import save_memory
                save_memory({})
                restored_files.append(filepath)
                
    if issues_found:
        log_error("HealthMonitor", f"Integrity check failed: {', '.join(issues_found)}")
        if restored_files:
            log_info("HealthMonitor", f"Successfully self-healed assets: {', '.join(restored_files)}")
        return False, issues_found, restored_files
        
    return True, [], []

def run_system_diagnostic() -> str:
    """Compiles a live health telemetry report of the active process environment."""
    file_status, missing, fixed = audit_file_integrity()
    active_threads = [t.name for t in threading.enumerate()]
    
    output = "\n"+"="*50+"\n"
    output += "               NOVA CORE DIAGNOSTIC LOG MATRIX\n"
    output += "="*50+"\n"
    output += f"  * Operational Status : {'[ HEALTHY ]' if file_status else '[ DEGRADED ]'}\n"
    output += f"  * Active Thread Count: {len(active_threads)}\n"
    output += f"  * Process Threads    : {', '.join(active_threads)}\n"
    output += f"  * File System State  : {'INTEGRAL' if file_status else 'RECOVERED'}\n"
    
    if missing:
        output += f"  * Found Anomalies   : {len(missing)} detected\n"
        for item in missing:
            output += f"    - {item}\n"
    if fixed:
        output += "  * Executed Fixes     :\n"
        for item in fixed:
            output += f"    - Re-seeded default structure for {item}\n"
            
    output += "="*50+"\n"
    return output

def safe_execute_tool(tool_callable, *args, **kwargs):
    """
    Wraps tool executions inside a fault-isolation chamber, preventing a
    broken tool from crashing Nova's primary interface shell.
    """
    try:
        return tool_callable(*args, **kwargs)
    except Exception as e:
        log_error("HealthMonitor", f"Fault Isolated! Intercepted error in {tool_callable.__name__}: {e}")
        print(f"\n[FAULT ISOLATION CHAMBER] Nova intercepted a runtime exception in execution loop.")
        print(f"Details: {e}")
        print("Action Plan: Isolated component cleanly. Returning execution to main thread safely.")
        return None