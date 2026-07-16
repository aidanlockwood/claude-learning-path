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

def chat(messages, system = None, stream = False, output_config = None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "stream": stream
    }

    if system:
        params["system"] = system

    if output_config:
        params["output_config"] = output_config

    message = client.messages.create(**params)

    text_blocks = [
        block.text
        for block in message.content
        if hasattr(block, "text") and block.text
    ]

    if text_blocks:
        return "".join(text_blocks)

    raise ValueError("Model response did not include any text content")
