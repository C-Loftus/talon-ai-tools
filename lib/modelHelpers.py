import base64
import json
import os
from typing import Optional, Tuple

import requests
from talon import actions, app, clip, settings

from ..lib.pureHelpers import strip_markdown
from .modelState import GPTState
from .modelTypes import Data, Headers, Tool

""""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""


def messages_to_string(messages: list[dict[str, any]]) -> str:
    """Format messages as a string"""
    formatted_messages = []
    for message in messages:
        if message.get("type") == "image_url":
            formatted_messages.append("image")
        else:
            formatted_messages.append(message.get("text", ""))
    return "\n\n".join(formatted_messages)


def gpt_send_request(headers: Headers, data: Data):
    url = settings.get("user.model_endpoint")
    response = requests.post(url, headers=headers, data=json.dumps(data))

    match response.status_code:
        case 200:
            notify("GPT Task Completed")
            resp = response.json()["choices"][0]["message"]["content"].strip()
            formatted_resp = strip_markdown(resp)
            return format_message(formatted_resp)
        case _:
            notify("GPT Failure: Check the Talon Log")
            raise Exception(response.json())


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


def make_prompt_from_editor_ctx(ctx: str):
    """Add the editor context to the prompt"""
    if not ctx:
        return ""

    return (
        "\n The user is inside a code editor. Use the content of the editor to improve the response and make it tailored to the specific context. The content is as follows: \n\n\n"
        + ctx
    )


def format_message(content: str):
    return {"type": "text", "text": content}


def extract_message(content: dict[str, any]) -> str:
    return content.get("text", "")


def format_clipboard():
    clipped_image = clip.image()
    if clipped_image:
        data = clipped_image.encode().data()
        base64_image = base64.b64encode(data).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/;base64,{base64_image}"},
        }
    else:
        return format_message(clip.text())


def generate_payload(
    prompt: dict[str, any],
    content: dict[str, any],
    tools: Optional[list[Tool]] = None,
    modifier: str = "",
) -> Tuple[Headers, Data]:
    """Generate the headers and data for the OpenAI API GPT request.
    Does not return the URL given the fact not all openai-compatible endpoints support new features like tools
    """
    notification = "GPT Task Started"
    if len(GPTState.context) > 0:
        notification += ": Reusing Stored Context"
    if GPTState.thread_enabled:
        notification += ", Threading Enabled"

    notify(notification)
    TOKEN = get_token()

    language = actions.code.language()
    language_context = (
        f"\nThe user is currently in a code editor for {language}."
        if language != ""
        else None
    )
    application_context = f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}"
    snippet_context = (
        "\n\nPlease return the response as a snippet with placeholders. A snippet can control cursors and text insertion using constructs like tabstops ($1, $2, etc., with $0 as the final position). Linked tabstops update together. Placeholders, such as ${1:foo}, allow easy changes and can be nested (${1:another ${2:}}). Choices, using ${1|one,two,three|}, prompt user selection."
        if modifier == "snip"
        else None
    )
    additional_context = [
        {"type": "text", "text": item}
        for item in [
            language_context,
            make_prompt_from_editor_ctx(
                actions.user.a11y_get_context_of_editor(content)
            ),
            application_context,
            snippet_context,
        ]
        if item is not None
    ]

    reused_context = list(GPTState.context)
    if GPTState.thread_enabled:
        reused_context += GPTState.thread

    current_query = [prompt, content]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    data = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": settings.get("user.model_system_prompt")},
                ]
                + additional_context
                + [
                    {"type": "text", "text": item}
                    for item in actions.user.contextual_user_context()
                ],
            },
            {
                "role": "user",
                "content": reused_context + current_query,
            },
        ],
        "max_tokens": 2024,
        "temperature": settings.get("user.model_temperature"),
        "n": 1,
        "model": settings.get("user.openai_model"),
    }
    if tools is not None:
        data["tools"] = tools
    return headers, data


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


def paste_and_modify(formatted_message: str, modifier: str = ""):
    """Paste or insert the result of a GPT query in a special way, e.g. as a snippet or selected"""
    match modifier:
        case "snip":
            actions.user.insert_snippet(formatted_message)
        case "" | _:
            actions.user.paste(formatted_message)
