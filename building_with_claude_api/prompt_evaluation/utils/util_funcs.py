from anthropic import Anthropic
from statistics import mean
import json
import ast
import re

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
                    },
                    "format": { 
                        "type": "string",
                        "description": "The format that the test prompt, defined in the task, should aim to test/validate"
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
            "format": "json" or "python" or "regex"
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

def build_output_config(code_format):
    if code_format == "json":
        content_schema = {
            "type": "object",
            "additionalProperties": False
        }
    else:
        content_schema = {
            "type": "string"
        }

    return {
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["json", "python", "regex"]
                    },
                    "content": content_schema
                },
                "required": ["format", "content"],
                "additionalProperties": False
            }
        }
    }

def unwrap_structured_output(output):
    try:
        parsed_output = json.loads(output)
    except json.JSONDecodeError:
        return output

    if not isinstance(parsed_output, dict) or "content" not in parsed_output:
        return output

    content = parsed_output["content"]

    if isinstance(content, (dict, list)):
        return json.dumps(content)

    return content

def run_prompt(test_case): 
    # Step 1 - Running the prompt
    prompt = f"""
        Please solve the following task:

        {test_case['task']}

        * Respond only with Python, JSON, or plain regex
        * Do not add any comments or commentary or explanation
    """

    messages = []
    add_user_message(messages, prompt)

    # Step 2 (COMPLETED PREVIOUSLY) - Generate the Dataset

    # Step 3 - Feed through Claude
    output_config = build_output_config(test_case["format"])
    output = chat(messages, output_config = output_config)
    return unwrap_structured_output(output)

# Step 4 - Feed Claude Respnose through Grader
def run_test_case(test_case): 
    output = run_prompt(test_case)
    
    # TODO - Grading 
    model_grade = grade_by_model(test_case, output)
    model_score = model_grade['score']
    reasoning = model_grade['reasoning']

    syntax_score = grade_syntax(output, test_case)
    score = (model_score + syntax_score) / 2

    return { 
        'output' : output, 
        'test_case': test_case,
        'score': score,
        'reasoning': reasoning
    }

def run_eval(dataset):
    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    average_score = mean([result['score'] for result in results])
    print(average_score)

    return results

def grade_syntax(response, test_case):
    format = test_case['format']

    if format == 'json':
        return validate_json(response)
    if format == 'python': 
        return validate_python(response)
    if format == 'regex':
        return validate_regex(response)

def grade_by_model(test_case, output):
    eval_prompt = f"""
    You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

    Original Task:
    <task>
    {test_case["task"]}
    </task>

    Solution to Evaluate:
    <solution>
    {output}
    </solution>

    Output Format
    Provide your evaluation as a structured JSON object with the following fields, in this specific order:
    - "strengths": An array of 1-3 key strengths
    - "weaknesses": An array of 1-3 key areas for improvement
    - "reasoning": A concise explanation of your overall assessment
    - "score": A number between 1-10

    Respond with JSON. Keep your response concise and direct.
    Example response shape:
    {{
        "strengths": string[],
        "weaknesses": string[],
        "reasoning": string,
        "score": number
    }}
    """

    output_config = {
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "strengths": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "weaknesses": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "reasoning": {
                        "type": "string"
                    },
                    "score": {
                        "type": "number"
                    }
                },
                "required": ["strengths", "weaknesses", "reasoning", "score"],
                "additionalProperties": False
            }
        }
    }

    messages = []

    add_user_message(messages, eval_prompt)

    eval_text = chat(messages, output_config = output_config)

    return json.loads(eval_text)

def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError: 
        return 0

def validate_python(text):
    try: 
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_regex(text):
    try: 
        re.compile(text.strip())
        return 10
    except re.error:
        return 0
