import json
from typing import Any, Optional

import requests
from talon import Module, actions

from ...lib.modelHelpers import generate_payload, notify
from ...lib.modelTypes import ChatCompletionResponse, InsertOption, Message
from .gpt_callables import (
    display_response,
    function_specs,
    insert_response,
    notify_user,
    search_for_command,
)

mod = Module()


def gpt_function_query(
    prompt: str,
    content: str,
    insert_response: InsertOption = InsertOption.PASTE,
    cursorless_destination: Optional[Any] = None,
) -> None:
    # Function calling likely to not be supported in local models so better to use OpenAI
    url = "https://api.openai.com/v1/chat/completions"

    headers, data = generate_payload(prompt, content, function_specs)

    response = requests.post(url, headers=headers, data=json.dumps(data))

    match response.status_code:
        case 200:
            notify("GPT Task Completed")
            payload: ChatCompletionResponse = response.json()
            result = payload["choices"][0]["message"]
            process_function_calls(result, insert_response, cursorless_destination)
        case _:
            notify("GPT Failure: Check API Key, Model, or Prompt")
            raise Exception(f"GPT Failure at POST request: {response.json()}")


def process_function_calls(
    message: Message,
    insertion_type: InsertOption,
    cursorless_destination: Optional[Any] = None,
):
    try:
        tool_calls = message["tool_calls"]
    except KeyError:
        notify("No tool calls were found in LLM response")
        print(message)
        return

    for tool in tool_calls:
        try:
            arguments = json.loads(tool["function"]["arguments"])
            first_argument = arguments[list(arguments.keys())[0]]

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
                match insertion_type:
                    case InsertOption.PASTE:
                        insert_response(first_argument)
                    case InsertOption.CURSORLESS:
                        actions.user.cursorless_insert(
                            cursorless_destination, first_argument
                        )
                    case InsertOption.KEY_PRESSES:
                        actions.insert(first_argument)
            # Just insert everything else since sometimes if will return
            # the language as the function name
            case _:
                insert_response(first_argument)


@mod.action_class
class UserActions:
    def gpt_dynamic_request(utterance: str, selected_text: str) -> None:
        """Run a query with dynamic function calls and paste the result"""
        gpt_function_query(utterance, selected_text)

    def gpt_dynamic_request_cursorless(
        utterance: str, selected_text: list[str], cursorless_destination: Any
    ) -> None:
        """Run a query with dynamic function calls and insert the result with cursorless"""
        if cursorless_destination == 0:
            gpt_function_query(
                utterance,
                " ".join(selected_text),
                InsertOption.PASTE,
                cursorless_destination=None,
            )
        else:
            gpt_function_query(
                utterance,
                " ".join(selected_text),
                InsertOption.CURSORLESS,
                cursorless_destination,
            )
