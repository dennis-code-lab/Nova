import threading
import time
from modules.logger import log_info, log_error

_jobs = {}
_scheduler_thread = None
_running = False

def add_job(name, callback, interval_seconds):
    """Registers a recurring background job with a specified execution interval."""
    _jobs[name] = {
        "callback": callback,
        "interval": interval_seconds,
        "last_run": 0
    }
    log_info("Scheduler", f"Successfully scheduled background job: [{name}] every {interval_seconds}s")

def _scheduler_loop():
    global _running
    while _running:
        current_time = time.time()
        for name, job_config in _jobs.items():
            if current_time - job_config["last_run"] >= job_config["interval"]:
                try:
                    # Update timestamp before running to prevent overlap if it takes time
                    job_config["last_run"] = current_time
                    log_info("Scheduler", f"Spawning background execution worker thread for job: [{name}]")
                    
                    # Spin up each individual task execution into its own lightweight worker thread
                    worker = threading.Thread(target=job_config["callback"], daemon=True)
                    worker.start()
                except Exception as e:
                    log_error("Scheduler", f"Failed to dispatch background job [{name}]: {e}")
        time.sleep(1)  # Precise tick check every second

def start_scheduler():
    """Ignites the core non-blocking background scheduling daemon."""
    global _scheduler_thread, _running
    if _running:
        return
    _running = True
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _scheduler_thread.start()
    log_info("Scheduler", "Dynamic Background Job Scheduler Engine activated.")

def stop_scheduler():
    """Gracefully terminates the scheduler event loop execution context."""
    global _running
    _running = False
    log_info("Scheduler", "Dynamic Background Job Scheduler Engine deactivated.")