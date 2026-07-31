import os


def save_note(filename, content):

    with open(
        f"notes/{filename}.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    return "Note saved."


def read_note(filename):

    try:

        with open(
            f"notes/{filename}.txt",
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except Exception:

        return "Note not found."


def list_notes():

    files = os.listdir("notes")

    notes = []

    for file in files:

        if file.endswith(".txt"):

            notes.append(file[:-4])

    if notes:

        return ", ".join(notes)

    return "No notes found."
