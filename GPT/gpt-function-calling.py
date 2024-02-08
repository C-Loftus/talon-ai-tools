from talon import Module, actions, app, settings
from typing import Callable
import requests
import os
import json
from .gpt import notify
from .lib import HTMLbuilder

mod = Module()

def gpt_function_query(prompt: str, content: str, insert_response: Callable[[str], str]) -> str:
    notify("GPT Task Started")

    try:
        TOKEN = os.environ["OPENAI_API_KEY"]
    except:
        notify("GPT Failure: env var OPENAI_API_KEY is not set.")
        return ""

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

    message = response.json()["choices"][0]["message"]
    if response.status_code == 200:
        notify("GPT Task Completed")
        print(response.json())
        process_function_calls(insert_response, message)

        content = (message["content"] or "").strip()
        if len(content) != 0:
            actions.user.display_response(content)

    else:
        notify("GPT Failure: Check API Key, Model, or Prompt")
        print(response.json())

def process_function_calls(insert_response, message):
    try:
        tool_calls = message["tool_calls"]
        while tool_calls:
            tool = tool_calls.pop()
            first_argument = tool['function']['arguments']
            try:
                first_argument = json.loads(first_argument)['str']
            except Exception as e:
                notify(f"Argument Jason was malformed: {e}")
            match tool['function']['name']:
                case 'insert':
                    insert_response(first_argument)
                case 'display':
                    actions.user.display_response(first_argument)
                case 'notify':
                    actions.user.notify_user(first_argument)
                case 'search_for_command':
                    actions.user.search_for_command(first_argument)
    except Exception as e:
        notify(f"No tool_calls found in response from LLM: {e}")

@mod.action_class
class UserActions:
    def gpt_go(utterance: str, selected_text: str) -> str:
        """Run a query against ChatGPT and allow it to execute targeted function calls on your machine"""

        return gpt_function_query(utterance, selected_text, actions.user.paste)

    def gpt_go_cursorless(utterance: str, text_to_process: str, cursorless_destination: any):
        """Apply a cursorless prompt"""
        def insert_to_destination(result: str):
            actions.user.cursorless_insert(cursorless_destination, result)
        return gpt_function_query(utterance, text_to_process, insert_to_destination)

    def notify_user(response: str):
        """Send a notification to the desktop"""
        actions.app.notify(response)

    def search_for_command(response: str):
        """Search VSCode for command"""
        actions.user.command_palette()
        actions.user.paste(response)

    def display_response(response: str):
        """Open the GPT help file in the web browser"""
        builder = HTMLbuilder.Builder()
        builder.h1("Displaying the Model Response")
        builder.p(response)
        builder.render()
