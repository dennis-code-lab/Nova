from plyer import notification

# Trigger the system notification
notification.notify(
    title="Nova Test",
    message="If you see this, notifications work.",
    timeout=10,
)

# Keep the console open so the script doesn't instantly close
input("Press Enter to exit...")