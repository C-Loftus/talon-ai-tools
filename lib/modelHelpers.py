import base64
import json
import os
from typing import Literal, Optional

import requests
from talon import actions, app, clip, settings

from ..lib.pureHelpers import strip_markdown
from .modelState import GPTState
from .modelTypes import GPTMessage, GPTMessageItem

""""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""


def messages_to_string(messages: list[GPTMessageItem]) -> str:
    """Format messages as a string"""
    formatted_messages = []
    for message in messages:
        if message.get("type") == "image_url":
            formatted_messages.append("image")
        else:
            formatted_messages.append(message.get("text", ""))
    return "\n\n".join(formatted_messages)


def thread_to_string(chats: list[GPTMessage]) -> str:
    """Format thread as a string"""
    formatted_messages = []
    for chat in chats:
        formatted_messages.append(chat.get("role"))
        formatted_messages.append(messages_to_string(chat.get("content", [])))
    return "\n\n".join(formatted_messages)


def notify(message: str):
    """Send a notification to the user. Defaults the Andreas' notification system if you have it installed"""
    try:
        actions.user.notify(message)
    except Exception:
        app.notify(message)
    # Log in case notifications are disabled
    print(message)


def get_token() -> str:
    """Get the OpenAI API key from the environment"""
    try:
        return os.environ["OPENAI_API_KEY"]
    except KeyError:
        message = "GPT Failure: env var OPENAI_API_KEY is not set."
        notify(message)
        raise Exception(message)


def format_messages(
    role: Literal["user", "system", "assistant"], messages: list[GPTMessageItem]
) -> GPTMessage:
    return {
        "role": role,
        "content": messages,
    }


def format_message(content: str) -> GPTMessageItem:
    return {"type": "text", "text": content}


def extract_message(content: GPTMessageItem) -> str:
    return content.get("text", "")


def format_clipboard() -> GPTMessageItem:
    clipped_image = clip.image()
    if clipped_image:
        data = clipped_image.encode().data()
        base64_image = base64.b64encode(data).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/;base64,{base64_image}"},
        }
    else:
        if not clip.text():
            raise RuntimeError(
                "User requested info from the clipboard but there is nothing in it"
            )

        return format_message(clip.text())  # type: ignore Unclear why this is not narrowing the type


def send_request(
    prompt: GPTMessageItem,
    content_to_process: Optional[GPTMessageItem],
    tools: Optional[list[dict[str, str]]] = None,
    destination: str = "",
):
    """Generate run a GPT request and return the response"""
    notification = "GPT Task Started"
    if len(GPTState.context) > 0:
        notification += ": Reusing Stored Context"
    if GPTState.thread_enabled:
        notification += ", Threading Enabled"

    notify(notification)
    TOKEN = get_token()

    language = actions.code.language()
    language_context = (
        f"The user is currently in a code editor for the programming language: {language}."
        if language != ""
        else None
    )
    application_context = f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}"
    snippet_context = (
        "\n\nPlease return the response as a snippet with placeholders. A snippet can control cursors and text insertion using constructs like tabstops ($1, $2, etc., with $0 as the final position). Linked tabstops update together. Placeholders, such as ${1:foo}, allow easy changes and can be nested (${1:another ${2:}}). Choices, using ${1|one,two,three|}, prompt user selection."
        if destination == "snip"
        else None
    )

    system_messages: list[GPTMessageItem] = [
        {"type": "text", "text": item}
        for item in [
            settings.get("user.model_system_prompt"),
            language_context,
            application_context,
            snippet_context,
        ]
        + actions.user.gpt_additional_user_context()
        if item is not None
    ]

    system_messages += GPTState.context

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    content: list[GPTMessageItem] = []
    if content_to_process is not None:
        if content_to_process["type"] == "image_url":
            image = content_to_process
            # If we are processing an image, we have
            # to add it as a second message
            content = [prompt, image]
        elif content_to_process["type"] == "text":
            # If we are processing text content, just
            # add the text on to the same message instead
            # of splitting it into multiple messages
            prompt["text"] = (
                prompt["text"] + '\n\n"""' + content_to_process["text"] + '"""'  # type: ignore a Prompt has to be of type text
            )
    else:
        # If there isn't any content to process,
        # we just use the prompt and nothing else
        content = [prompt]

    current_request: GPTMessage = {
        "role": "user",
        "content": content,
    }

    data = {
        "messages": [
            format_messages("system", system_messages),
        ]
        + GPTState.thread
        + [current_request],
        "max_tokens": 2024,
        "temperature": settings.get("user.model_temperature"),
        "n": 1,
        "model": settings.get("user.openai_model"),
    }

    if tools is not None:
        data["tools"] = tools

    url: str = settings.get("user.model_endpoint")  # type: ignore
    raw_response = requests.post(url, headers=headers, data=json.dumps(data))

    match raw_response.status_code:
        case 200:
            notify("GPT Task Completed")
            resp = raw_response.json()["choices"][0]["message"]["content"].strip()
            formatted_resp = strip_markdown(resp)
            response = format_message(formatted_resp)
        case _:
            notify("GPT Failure: Check the Talon Log")
            raise Exception(raw_response.json())

    if GPTState.thread_enabled:
        GPTState.push_thread(current_request)
        GPTState.push_thread(
            {
                "role": "assistant",
                "content": [response],
            }
        )

    return response


def get_clipboard_image():
    try:
        clipped_image = clip.image()
        if not clipped_image:
            raise Exception("No image found in clipboard")

        data = clipped_image.encode().data()
        base64_image = base64.b64encode(data).decode("utf-8")
        return base64_image
    except Exception as e:
        print(e)
        raise Exception("Invalid image in clipboard")
