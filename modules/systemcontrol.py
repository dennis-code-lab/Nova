import os


def lock_computer():
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Locking computer..."
    except Exception as e:
        return f"Error: {e}"


def restart_computer():
    try:
        os.system("shutdown /r /t 0")
        return "Restarting computer..."
    except Exception as e:
        return f"Error: {e}"


def shutdown_computer():
    try:
        os.system("shutdown /s /t 0")
        return "Shutting down computer..."
    except Exception as e:
        return f"Error: {e}"


def sleep_computer():
    try:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Putting computer to sleep..."
    except Exception as e:
        return f"Error: {e}"