from anthropic import Anthropic
import json

## From the multi turn conversations lesson
def api_client_setup(model = "claude-haiku-4-5"):
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

    return message.content[0].text

generate_dataset_output_schema = { 
    "format": { 
        "type": "json_schema", 
        "schema": { 
            "type": "array", 
            "items": { 
                "type": "object",
                "properties": { 
                    "task": { 
                        "type": "string",
                        "description": "A short natural-language description of the task."
                    }
                },
                "required": ["task"], 
                "additionalProperties": False
            }
        }
    }
}

def generate_dataset():
    prompt = """
    Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
    that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
    each representing task that requires Python, JSON, or a Regex to complete.

    Example output:
    ```json
    [
        {
            "task": "Description of task",
        },
        ...additional
    ]
    ```

    * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
    * Focus on tasks that do not require writing much code

    Please generate 3 objects.
    """
    messages = []
    add_user_message(messages, prompt)
    answer = chat(messages, output_config = generate_dataset_output_schema)

    return json.loads(answer)
