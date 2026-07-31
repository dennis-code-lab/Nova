import os


CHAT_FILE = "data/chat_history.txt"


def save_chat(message):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        CHAT_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            message + "\n"
        )


def load_chat():

    if not os.path.exists(
        CHAT_FILE
    ):

        return ""

    with open(
        CHAT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


def clear_chat_file():

    with open(
        CHAT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("")