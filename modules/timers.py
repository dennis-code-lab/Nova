import threading
import time
from modules.voice import speak

try:
    from plyer import notification
except Exception:
    notification = None


def start_timer(seconds):
    def timer_thread():
        time.sleep(seconds)
        message = f"Timer finished ({seconds} seconds)"

        print(f"\nNova: {message}")
        speak(message)

        if notification:
            notification.notify(
                title="Nova Timer", message=message, timeout=10
            )

    # Spawn the isolated background thread so the core app doesn't freeze
    threading.Thread(target=timer_thread, daemon=True).start()

    return f"Timer started for {seconds} seconds."