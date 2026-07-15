from anthropic import Anthropic

## From the multi turn conversations lesson
def api_client_setup(model = "claude-sonnet-5"):
    client = Anthropic()
    model = model

    return client, model

client, model = api_client_setup()

def add_user_message(messages, text):
    user_message = { 
        'role': 'user', 
        'content': text
    }
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = { 
        'role': 'assistant', 
        'content': text
    }
    messages.append(assistant_message)

def chat(messages, system = None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)

    return message.content[0].text