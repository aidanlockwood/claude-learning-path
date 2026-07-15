from anthropic import Anthropic

## From the multi turn conversations lesson
def api_client_setup():
    client = Anthropic()
    model = "claude-sonnet-5"

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

def chat(messages): 
    message = client.messages.create(
        model = model,
        max_tokens = 1000,
        messages = messages
    )
    return message.content[0].text