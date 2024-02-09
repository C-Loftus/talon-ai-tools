from talon import Module, actions, settings
from typing import Callable
import json
import os
import requests
from ..gpt import notify
from .gpt_callables import search_for_command, notify_user, display_response

mod = Module()

def gpt_function_query(prompt: str, content: str, insert_response: Callable[[str], str]) -> str:
    notify("GPT Task Started")

    try:
        TOKEN = os.environ["OPENAI_API_KEY"]
    except:
        notify("GPT Failure: env var OPENAI_API_KEY is not set.")
        raise Exception("GPT Failure")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": f"language:\n{actions.code.language()}",
            },
            {"role": "user", "content": f"{prompt}:\n{content}"},
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "insert",
                    "description": "insert(str: string) - this inserts the string into the document. The document is in the language specified so if you aren't careful you will cause syntax errors.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The text to insert",
                            }
                        },
                        "required": ["str"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "notify",
                    "description": "notify(str: string) - this notifies the user using a popup notification",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The text to notify",
                            }
                        },
                        "required": ["str"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "display",
                    "description": "display(str: string) - DEFAULT - this displays the response to the user. Use this for all informational text aside from notifications. Use this instead of returning content in the response.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The text to display",
                            }
                        },
                        "required": ["str"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_for_command",
                    "description": "search_for_command(str: string) - this searches for a command in the VSCode command palette. If I ask you to do something, please use this command to search for an appropriate command.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The command to search for",
                            }
                        },
                        "required": ["str"],
                    },
                },
            }
        ],
        "max_tokens": 2024,
        "temperature": 0.6,
        "n": 1,
        "stop": None,
        "model": settings.get("user.openai_model"),
    }


    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        notify("GPT Task Completed")
        message = response.json()["choices"][0]["message"]
        process_function_calls(insert_response, message)

        content = (message["content"] or "").strip()
        if len(content) != 0:
            display_response(content)

    else:
        notify("GPT Failure: Check API Key, Model, or Prompt")
        raise Exception(f"GPT Failure at POST request: {response.json()}")

def process_function_calls(insert_response, message):
    try:
        tool_calls = message["tool_calls"]
    except Exception as e:
        notify(f"No tool calls were found in LLM response")
        return

    for tool in tool_calls:

        try: 
            first_argument = tool['function']['arguments']
            first_argument = json.loads(first_argument)['str']
        except Exception as e:
            notify(f"Argument JSON was malformed: {e}")
            # Try next tool call if this one fails
            continue

        match tool['function']['name']:
            case 'insert':
                insert_response(first_argument)
            case 'display':
                display_response(first_argument)
            case 'notify':
                notify_user(first_argument)
            case 'search_for_command':
                search_for_command(first_argument)


@mod.action_class
class UserActions:
    def gpt_can_you(utterance: str, selected_text: str) -> str:
        """Run a query with function calls and insert the result"""
        return gpt_function_query(utterance, selected_text, actions.user.paste)

    def gpt_can_you_cursorless(utterance: str, text_to_process: str, cursorless_destination: any):
        """Run a query with function calls and insert the result using cursorless"""
        def insert_to_destination(result: str):
            actions.user.cursorless_insert(cursorless_destination, result)
        return gpt_function_query(utterance, text_to_process, insert_to_destination)

    