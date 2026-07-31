import os

NOTES_FOLDER = "notes"


def search_notes(keyword):
    keyword = keyword.lower()

    if not os.path.exists(NOTES_FOLDER):
        return "No notes folder found."

    matches = []

    for file in os.listdir(NOTES_FOLDER):
        path = os.path.join(NOTES_FOLDER, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Matches if keyword is in either the file name or file text content
            if keyword in file.lower() or keyword in content.lower():
                matches.append(file)

        except Exception:
            pass

    if not matches:
        return "No matching notes found."

    return "Matching notes:\n" + "\n".join(matches)