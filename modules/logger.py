from datetime import datetime
import os
import traceback

LOG_FILE = "data/runtime.log"

def log_event(level, component, message, include_traceback=False):
    """Writes system runtime events to a local diagnostic log file."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] [{level.upper()}] [{component}]: {message}\n"
    
    # If it's a crash, capture the exact file line numbers causing it
    if include_traceback:
        log_entry += f"{traceback.format_exc()}\n"
        log_entry += f"{'-'*60}\n" # Visually separates tracebacks in your text file
        
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def log_info(component, message):
    log_event("INFO", component, message)

def log_error(component, message):
    # Automatically tracks the error type and full execution stack trace!
    log_event("ERROR", component, message, include_traceback=True)