from datetime import datetime
import threading
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from modules.ai import ask_ai
from modules.chat_history import clear_chat_file, load_chat, save_chat
from modules.conversation import clear_history
from modules.listener import listen
from modules.reminders import check_reminders
from modules.voice import speak


def timestamp():
    return datetime.now().strftime("%H:%M:%S")


def add_message(sender, message):
    text = f"[{timestamp()}] {sender}: {message}"
    chat_area.config(state="normal")
    chat_area.insert(tk.END, text + "\n\n")
    chat_area.see(tk.END)
    chat_area.config(state="disabled")
    save_chat(text)


def set_status(text):
    status_label.config(text=f"Status: {text}")
    root.update()


def send_message():
    user_message = entry.get().strip()
    if not user_message:
        return

    entry.delete(0, tk.END)
    add_message("You", user_message)
    set_status("Thinking...")

    try:
        answer = ask_ai(user_message)
    except Exception as e:
        answer = f"Error: {e}"

    add_message("Nova", answer)
    speak(answer)
    set_status("Ready")


def voice_input():
    set_status("Listening...")
    result = listen()

    if not result:
        result = "Sorry, I could not understand."

    add_message("You (Voice)", result)
    set_status("Ready")

    if result != "Sorry, I could not understand.":
        set_status("Thinking...")
        answer = ask_ai(result)
        add_message("Nova", answer)
        speak(answer)
        set_status("Ready")


def clear_chat():
    clear_history()
    clear_chat_file()
    chat_area.config(state="normal")
    chat_area.delete("1.0", tk.END)
    chat_area.config(state="disabled")
    add_message("Nova", "Conversation cleared.")
    set_status("Ready")


def reminder_worker():
    while True:
        reminder = check_reminders()
        if reminder:
            root.after(0, lambda r=reminder: add_message("Nova", r))
            speak(reminder)
        time.sleep(30)


# --- GUI Setup ---
root = tk.Tk()
root.title("Nova AI Assistant")
root.geometry("1000x700")

BG = "#1E1E1E"
FG = "#FFFFFF"
ENTRY_BG = "#2D2D2D"
BUTTON_BG = "#3A3A3A"
root.configure(bg=BG)

chat_area = ScrolledText(
    root,
    wrap=tk.WORD,
    bg=BG,
    fg=FG,
    insertbackground=FG,
    font=("Consolas", 11),
)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.config(state="disabled")

entry = tk.Entry(
    root, bg=ENTRY_BG, fg=FG, insertbackground=FG, font=("Arial", 12)
)
entry.pack(padx=10, pady=5, fill=tk.X)

button_frame = tk.Frame(root, bg=BG)
button_frame.pack(pady=5)

send_button = tk.Button(
    button_frame, text="Send", bg=BUTTON_BG, fg=FG, command=send_message
)
send_button.pack(side=tk.LEFT, padx=5)

listen_button = tk.Button(
    button_frame, text="🎤 Listen", bg=BUTTON_BG, fg=FG, command=voice_input
)
listen_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(
    button_frame, text="🧹 Clear Chat", bg=BUTTON_BG, fg=FG, command=clear_chat
)
clear_button.pack(side=tk.LEFT, padx=5)

status_label = tk.Label(root, text="Status: Ready", bg=BG, fg=FG, anchor="w")
status_label.pack(fill=tk.X, padx=10, pady=5)

# FIXED: Corrected key-binding parameter from "" to "<Return>"
entry.bind("<Return>", lambda event: send_message())

# --- Initialize Data ---
history = load_chat()
chat_area.config(state="normal")
if history:
    chat_area.insert(tk.END, history + "\n\n")
else:
    chat_area.insert(
        tk.END,
        f"[{timestamp()}] Nova: Hello Dennis! How can I help you today?\n\n",
    )
chat_area.config(state="disabled")

# --- Start Background Worker ---
threading.Thread(target=reminder_worker, daemon=True).start()

root.mainloop()