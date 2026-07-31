import os
from modules import registry
from modules.profiler import get_profile_report

# Global in-memory cache for the last run telemetry variables
_telemetry_cache = {
    "target_goal": "None",
    "loops_burned": 0,
    "finish_status": "Idle",
    "step_traces": []
}

def update_telemetry(goal, loops, status, traces):
    """Updates the global telemetry cache with variables from the last run."""
    _telemetry_cache["target_goal"] = goal
    _telemetry_cache["loops_burned"] = loops
    _telemetry_cache["finish_status"] = status
    _telemetry_cache["step_traces"] = traces

def display_dashboard():
    """Compiles active system variables into a clean developer matrix view."""
    
    # Safely extract registered system services from registry
    active_services = []
    registry_dict = {}
    for attr_name in ["services", "SERVICES", "_services", "registry_map"]:
        if hasattr(registry, attr_name):
            target = getattr(registry, attr_name)
            if isinstance(target, dict):
                registry_dict = target
                break
                
    if registry_dict:
        active_services = list(registry_dict.keys())
        
    # Read the active performance metrics profile report
    perf_metrics = get_profile_report()
    
    # Extract active thread count
    import threading
    active_threads = threading.active_count() - 1 # Subtract main thread for worker count

    dashboard = f"""
============================================================
         NOVA CORE ARCHITECTURE DEVELOPER CONSOLE          
============================================================

[SYSTEM INFRASTRUCTURE STATUS]
  - Active Service Registry Tracks : {len(active_services)}
  - Registered Active Services    : {active_services}
  - Background Thread Count       : {active_threads}

[GROUNDING KNOWLEDGE BASE]
  - favorite_color: green
  - favorite_team: Arsenal
  - name: Dennis

[PIPELINE PERFORMANCE PROFILING]
"""
    if perf_metrics:
        for module, lap in perf_metrics.items():
            dashboard += f"  - latency://{module.ljust(20)} : {lap}\n"
    else:
        dashboard += "  - No active performance profiling metrics cached yet.\n"

    dashboard += f"""
[LAST AUTOMATED LIFECYCLE TELEMETRY]
  - Target Goal   : {_telemetry_cache['target_goal']}
  - Loops Burned  : {_telemetry_cache['loops_burned']} attempts
  - Finish Status : {_telemetry_cache['finish_status']}
  - Step Traces   : {_telemetry_cache['step_traces']}
============================================================
"""
    return dashboard