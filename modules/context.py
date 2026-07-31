context_data = {}


def set_context(key, value):
    context_data[key] = value


def get_context(key):
    return context_data.get(key)


def clear_context():
    context_data.clear()