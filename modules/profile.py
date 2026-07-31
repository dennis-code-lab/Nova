import json
import os

PROFILE_FILE = "data/profile.json"


def load_profile():

    if not os.path.exists(PROFILE_FILE):

        return {}

    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_profile(profile):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        PROFILE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4
        )


def remember_fact(key, value):

    profile = load_profile()

    profile[key] = value

    save_profile(profile)

    return "I'll remember that."


def get_fact(key):

    profile = load_profile()

    return profile.get(key)


def list_facts():

    return load_profile()


def profile_to_text():

    profile = load_profile()

    if not profile:

        return "No known user facts."

    text = ""

    for key, value in profile.items():

        text += f"{key}: {value}\n"

    return text