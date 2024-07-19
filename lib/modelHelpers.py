import base64
import os
from typing import Optional, Tuple

from talon import actions, app, clip, settings

from .modelTypes import Data, Headers, Tool

""""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""


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


def generate_payload(
    prompt: str, content: str, tools: Optional[list[Tool]] = None
) -> Tuple[Headers, Data]:
    """Generate the headers and data for the OpenAI API GPT request.
    Does not return the URL given the fact not all openai-compatible endpoints support new features like tools
    """
    notify("GPT Task Started")

    TOKEN = get_token()

    language = actions.code.language()
    additional_context = (
        f"\nThe user is currently in a code editor for {language}."
        if language != ""
        else ""
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    message = {"type": "text", "text": content}
    if content == "__IMAGE__":
        clipped_image = clip.image()
        if clipped_image:
            data = clipped_image.encode().data()
            base64_image = base64.b64encode(data).decode("utf-8")
            message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            }

    data = {
        "messages": [
            {
                "role": "system",
                "content": settings.get("user.model_system_prompt")
                + additional_context,
            },
            {"role": "user", "content": [{"type": "text", "text": prompt}, message]},
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
