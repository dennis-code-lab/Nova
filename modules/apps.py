import os


def open_app(app_name):
    app_name = app_name.lower()

    try:
        # --- Native Desktop Applications ---
        if app_name == "notepad":
            os.system("start notepad")
        elif app_name == "calculator":
            os.system("start calc")
        elif app_name == "paint":
            os.system("start mspaint")
        elif app_name == "chrome":
            os.system("start chrome")
        elif app_name == "explorer":
            os.system("start explorer")
        elif app_name == "vscode":
            os.system("start code")

        # --- Web Applications & URLs ---
        elif app_name == "youtube":
            os.system("start https://www.youtube.com")
        elif app_name == "gmail":
            os.system("start https://mail.google.com")
        elif app_name == "github":
            os.system("start https://github.com")
        elif app_name == "chatgpt":
            os.system("start https://chatgpt.com")
        elif app_name == "google":
            os.system("start https://www.google.com")

        else:
            return "Unknown application."

        return f"Opening {app_name}..."

    except Exception as e:
        return f"Error opening application: {e}"