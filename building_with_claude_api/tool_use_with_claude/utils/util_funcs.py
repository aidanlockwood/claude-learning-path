from pathlib import Path
from anthropic import Anthropic
from datetime import datetime
from dotenv import load_dotenv
from anthropic.types import ToolParam

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

## From the multi turn conversations lesson
def api_client_setup(model = "claude-haiku-4-5"):
    client = Anthropic()

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

def chat(messages, 
         system = None, 
         stream = False, 
         output_config = None,
         tools = None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "stream": stream,
    }

    if tools: 
        params['tools'] = tools

    if system:
        params["system"] = system

    if output_config:
        params["output_config"] = output_config

    message = client.messages.create(**params)
    return message

def text_from_message(message):
    return "\n".join( 
        [block.text for block in message.content if block.type == 'text']
    )

get_current_datetime_schema = ToolParam({
  "name": "get_current_datetime",
  "description": "Return the current local datetime from the runtime environment as a formatted string. Use this tool when the user asks for the current date, time, or a current datetime in a custom format. Do not use it for date arithmetic, future/past calculations, or timezone conversion. The optional date_format parameter must be a non-empty Python strftime format string. If omitted, the tool uses '%Y-%m-%d %H:%M:%S'.",
  "strict": True,
  "input_schema": {
    "type": "object",
    "properties": {
      "date_format": {
        "type": "string",
        "minLength": 1,
        "description": "Optional Python strftime format string used to format the current datetime. Must not be empty. Defaults to '%Y-%m-%d %H:%M:%S'. Example: '%A, %B %d, %Y %I:%M:%S %p'.",
        "default": "%Y-%m-%d %H:%M:%S"
      }
    },
    "additionalProperties": False
  },
  "input_examples": [
    {},
    {
      "date_format": "%A, %B %d, %Y %I:%M:%S %p"
    }
  ]
})

def get_current_datetime(date_format = "%Y-%m-%d %H:%M:%S"): 
    if not date_format: 
        raise ValueError('date_format cannot be empty')
    return datetime.now().strftime(date_format)
