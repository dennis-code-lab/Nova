import speech_recognition as sr


def listen():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("Nova: Listening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        audio = recognizer.listen(source)

    try:

        text = recognizer.recognize_google(audio)

        return text

    except Exception:

        return "Sorry, I could not understand."
