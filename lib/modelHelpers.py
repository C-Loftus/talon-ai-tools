import base64
import json
import os
from typing import Optional, Tuple

import requests
from talon import actions, app, clip, settings

from ..lib.pureHelpers import strip_markdown
from .modelTypes import Data, Headers, Tool

""""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""


stored_context = []
thread_context = []


def clear_context():
    """Reset the stored context"""
    global stored_context
    stored_context = []
    actions.app.notify("Cleared user context")


def new_thread():
    """Create a new thread"""
    global thread_context
    thread_context = []
    actions.app.notify("Created a new thread")


def push_context(context: str):
    """Add the selected text to the stored context"""
    global stored_context
    stored_context += [format_message(context)]
    actions.app.notify("Appended user context")


def push_thread(context: str):
    """Add the selected text to the stored context"""
    global thread_context
    thread_context += [format_message(context)]
    actions.app.notify("Appended to thread")


def optimize_thread():
    """Optimize the context for reducing the space"""
    global thread_context
    prompt = "Please summarize this conversation to shorten it. I'm going to pass it back to you so this is only for your consumption. Make it as short as possible."

    headers, data = generate_payload(prompt, "")
    thread_context = [format_message(gpt_send_request(headers, data))]
    actions.app.notify("Optimized thread context")


def optimize_context():
    """Optimize the context for reducing the space"""
    global stored_context
    prompt = "Please summarize this conversation to shorten it. I'm going to pass it back to you so this is only for your consumption. Make it as short as possible."

    headers, data = generate_payload(prompt, "")
    stored_context = [format_message(gpt_send_request(headers, data))]
    actions.app.notify("Optimized user context")


def messages_to_string(messages: list[dict[str, any]]) -> str:
    """Format messages as a string"""
    formatted_messages = []
    for message in messages:
        if message.get("type") == "image_url":
            formatted_messages.append("image")
        else:
            formatted_messages.append(message.get("text", ""))
    return "\n\n".join(formatted_messages)


def string_context():
    """Format the context for display"""
    global stored_context
    return messages_to_string(stored_context)


def string_thread():
    """Format the thread for display"""
    global thread_context
    return messages_to_string(thread_context)


def gpt_send_request(headers: Headers, data: Data):
    url = settings.get("user.model_endpoint")
    response = requests.post(url, headers=headers, data=json.dumps(data))

    match response.status_code:
        case 200:
            notify("GPT Task Completed")
            resp = response.json()["choices"][0]["message"]["content"].strip()
            formatted_resp = strip_markdown(resp)
            return formatted_resp
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
    message = {"type": "text", "text": content}
    if content == "__IMAGE__":
        clipped_image = clip.image()
        if clipped_image:
            data = clipped_image.encode().data()
            base64_image = base64.b64encode(data).decode("utf-8")
            message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/;base64,{base64_image}"},
            }
    return message


def generate_payload(
    prompt: str, content: str, tools: Optional[list[Tool]] = None, modifier: str = ""
) -> Tuple[Headers, Data]:
    """Generate the headers and data for the OpenAI API GPT request.
    Does not return the URL given the fact not all openai-compatible endpoints support new features like tools
    """
    global stored_context
    global thread_context
    notification = "GPT Task Started"
    if len(stored_context) > 0:
        notification += ": Reusing Stored Context"
    notify(notification)
    TOKEN = get_token()

    language = actions.code.language()

    additional_context = [
        {"type": "text", "text": item}
        for item in [
            (
                f"\nThe user is currently in a code editor for {language}."
                if language != ""
                else ""
            )
            + make_prompt_from_editor_ctx(
                actions.user.a11y_get_context_of_editor(content)
            )
            + f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}"
        ]
    ]
    reused_context = stored_context
    if modifier == "thread":
        reused_context += thread_context

    current_query = [{"type": "text", "text": prompt}]
    if content != "__CONTEXT__":
        current_query += [format_message(content)]

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


def paste_and_modify(result: str, modifier: str = ""):
    """Paste or insert the result of a GPT query in a special way, e.g. as a snippet or selected"""
    match modifier:
        case "snip":
            actions.user.insert_snippet(result)
        case "" | _:
            actions.user.paste(result)

    # Snip is mutually exclusive with pasting, but chain can be run additionally after pasting
    if modifier == "chain":
        actions.user.gpt_select_last()
