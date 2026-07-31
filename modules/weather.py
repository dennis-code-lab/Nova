import requests


def get_weather(city):
    try:
        city = city.strip()
        url = f"https://wttr.in/{city}?format=3"

        # Using curl user-agent ensures wttr.in returns clean plain text
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "curl"},
        )

        weather_text = response.text.strip()

        # Block HTML content pages gracefully if service redirects
        if (
            "<html" in weather_text.lower()
            or "<doctype" in weather_text.lower()
        ):
            return (
                "Weather service returned an invalid response. "
                "Please try again later."
            )

        # Block known wttr.in internal error strings
        if weather_text.startswith("ERR"):
            return "Weather service is temporarily unavailable."

        return weather_text

    except requests.Timeout:
        return "Weather request timed out."

    except requests.ConnectionError:
        return "Unable to connect to weather service."

    except Exception as e:
        return f"Weather error: {e}"