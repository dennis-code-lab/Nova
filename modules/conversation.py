conversation_history = []


def add_message(role, content):

    conversation_history.append(
        {
            "role": role,
            "content": content
        }
    )

    if len(conversation_history) > 10:

        conversation_history.pop(0)


def get_history():

    return conversation_history


def clear_history():

    conversation_history.clear()