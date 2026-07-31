import time
from modules.logger import log_info

# Global registry to hold the execution durations of the latest run
_profile_cache = {}

def start_timer(module_name: str):
    """Marks the exact start timestamp for a specific pipeline block."""
    _profile_cache[module_name] = {
        "start": time.perf_counter(),
        "duration": 0.0
    }

def stop_timer(module_name: str):
    """Calculates the total elapsed execution duration for a module block."""
    if module_name in _profile_cache and "start" in _profile_cache[module_name]:
        end_time = time.perf_counter()
        duration = end_time - _profile_cache[module_name]["start"]
        _profile_cache[module_name]["duration"] = duration
        log_info("ProfilerEngine", f"Module '{module_name}' executed in {duration:.4f}s")

def get_profile_report() -> dict:
    """Returns the parsed latency records for the latest execution run."""
    report = {}
    for module, metrics in _profile_cache.items():
        report[module] = f"{metrics['duration']:.4f} seconds"
    return report