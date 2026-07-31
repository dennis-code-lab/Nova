import webbrowser


def web_search(query):

    search_url = (
        "https://www.google.com/search?q="
        + query.replace(" ", "+")
    )

    webbrowser.open(search_url)

    return (
        f"Searching Google for: {query}"
    )