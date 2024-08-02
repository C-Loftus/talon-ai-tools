import base64
import json
import os
from typing import ClassVar, Optional, Tuple

import requests
from talon import actions, app, clip, settings

from ..lib.pureHelpers import strip_markdown
from .modelTypes import Data, Headers, Tool

""""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""


class GPTState:
    text_to_confirm: ClassVar[str] = ""
    last_response: ClassVar[str] = ""
    last_was_pasted: ClassVar[bool] = False
    thread: ClassVar[str] = ""
    context: ClassVar[str] = ""

    @classmethod
    def push_thread(cls, thread_text: str):
        cls.thread += thread_text + "\n\n"
        actions.app.notify("Pushed thread context")

    @classmethod
    def push_context(cls, context: str):
        """Add the selected text to the stored context"""
        cls.context += context + "\n\n"
        actions.app.notify("Appended user context")

    @classmethod
    def new_thread(cls):
        """Create a new thread"""
        cls.thread = ""
        actions.app.notify("Created a new thread")

    @classmethod
    def clear_context(cls):
        cls.context = ""
        actions.app.notify("Cleared user context")


def summarize_context(context):
    """Optimize the context for reducing the space"""
    prompt = "Please summarize this conversation to shorten it. I'm going to pass it back to you so this is only for your consumption. Make it as short as possible."
    headers, data = generate_payload(prompt, context)

    stored_context = [format_message(gpt_send_request(headers, data))]
    actions.app.notify("Summarized user context")
    return stored_context


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
    """Send a request to the GPT model"""
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


def format_message(content: str) -> dict[str, dict | str]:
    """Format the message for the OpenAI API based on the content type of the input"""
    match content:
        case "__IMAGE__":
            clipped_image = clip.image()
            if clipped_image:
                data = clipped_image.encode().data()
                base64_image: str = base64.b64encode(data).decode("utf-8")
                message: dict[str, dict[str, str] | str] = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/;base64,{base64_image}"},
                }
                return message
            else:
                notify("User asked for an image, but there was no image stored")
                raise RuntimeError
        case _:
            return {"type": "text", "text": content}


def generate_payload(
    prompt: str, content: str, tools: Optional[list[Tool]] = None, modifier: str = ""
) -> Tuple[Headers, Data]:
    """Generate the headers and data for the OpenAI API GPT request.
    Does not return the URL given the fact not all openai-compatible endpoints support new features like tools
    """

    if len(GPTState.context) > 0:
        notify("GPT Task Started: Reusing stored context")
    else:
        notify("GPT Task Started")

    language = actions.code.language()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
    }

    background_info = (
        (
            f"\nThe user is currently in a code editor for {language}."
            if language != ""
            else ""
        )
        + make_prompt_from_editor_ctx(actions.user.a11y_get_context_of_editor(content))
        + f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}"
    )

    allMessages = []
    system_prompt = {
        "role": "system",
        "content": settings.get("user.model_system_prompt") + background_info,
    }

    allMessages.append(system_prompt)

    if modifier == "thread":
        thread_conversation = {
            "role": "user",
            "content": "The user has had a previous conversation with you. Here are their questions and your previous associated responses: \n\n"
            + GPTState.thread,
        }
        allMessages.append(thread_conversation)

    if GPTState.context:
        added_context = {
            "role": "user",
            "content": f"Note the following context: {GPTState.context}",
        }
        if actions.user.gpt_custom_user_context():
            added_context["content"] += "as well as " + " ".join(
                actions.user.gpt_custom_user_context()
            )

        allMessages.append(added_context)

    current_query = {"role": "user", "content": f"{prompt}\n\n{content}"}
    allMessages.append(current_query)

    data = {
        "messages": allMessages,
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
