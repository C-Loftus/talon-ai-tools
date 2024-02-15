import json
import os
from typing import Callable

import requests
from talon import Module, actions, settings

from ..gpt import notify
from .gpt_callables import (
    display_response,
    function_specs,
    notify_user,
    search_for_command,
)

mod = Module()


def gpt_function_query(
    prompt: str, content: str, insert_response: Callable[[str], str]
) -> str:
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
        "tools": function_specs,
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
        print(message)
        return

    for tool in tool_calls:

        try:
            first_argument = tool["function"]["arguments"]
            first_argument = json.loads(first_argument)
            first_argument = first_argument[list(first_argument.keys())[0]]

        except Exception as e:
            print(tool)
            notify(f"Argument JSON was malformed: {e}")
            break

        match tool["function"]["name"]:
            case "display_response":
                display_response(first_argument)
            case "notify_user":
                notify_user(first_argument)
            case "search_for_command":
                search_for_command(first_argument)
            case "insert_response":
                insert_response(first_argument)
            # Just insert everything else since sometimes if will return
            # the language as the function name
            case _:
                insert_response(first_argument)


@mod.action_class
class UserActions:
    def gpt_can_you(utterance: str, selected_text: str) -> str:
        """Run a query with function calls and insert the result"""
        return gpt_function_query(utterance, selected_text, actions.user.paste)

    def gpt_can_you_cursorless(
        utterance: str, text_to_process: str, cursorless_destination: any
    ):
        """Run a query with function calls and insert the result using cursorless"""
        if cursorless_destination == 0:
            return gpt_function_query(utterance, text_to_process, actions.user.paste)

        def insert_to_destination(result: str):
            actions.user.cursorless_insert(cursorless_destination, result)

        return gpt_function_query(utterance, text_to_process, insert_to_destination)
