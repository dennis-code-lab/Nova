import random


def handle_greeting(text):
    lower = text.lower().strip()

    greetings = {
        "hello": [
            "Hello Dennis!",
            "Hi Dennis!",
            "Hello! How can I help you today?",
        ],
        "hi": [
            "Hi Dennis!",
            "Hello!",
            "Nice to see you.",
        ],
        "good morning": [
            "Good morning Dennis!",
            "Good morning. Ready for a productive day?",
            "Morning Dennis!",
        ],
        "good afternoon": [
            "Good afternoon Dennis!",
            "Hope your day is going well.",
            "Good afternoon.",
        ],
        "good evening": [
            "Good evening Dennis!",
            "Good evening. How can I help?",
            "Hope you had a good day.",
        ],
        "goodnight": [
            "Goodnight Dennis.",
            "Sleep well.",
            "Have a restful night.",
        ],
        "how are you": [
            "I'm doing great and ready to help.",
            "I'm functioning perfectly.",
            "I'm doing well, thanks for asking.",
        ],
        "thank you": [
            "You're welcome.",
            "Happy to help.",
            "Anytime Dennis.",
        ],
        "thanks": [
            "You're welcome.",
            "Glad I could help.",
            "Anytime.",
        ],
    }

    # Direct exact phrase match lookup
    if lower in greetings:
        return random.choice(greetings[lower])

    # Smart conversational fallback fall-throughs
    if lower.startswith("good morning"):
        return random.choice(greetings["good morning"])

    if lower.startswith("good afternoon"):
        return random.choice(greetings["good afternoon"])

    if lower.startswith("good evening"):
        return random.choice(greetings["good evening"])

    if "thank you" in lower or lower.startswith("thanks"):
        return random.choice(greetings["thanks"])

    return None