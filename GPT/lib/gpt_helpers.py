import os
import platform
import re
from typing import Optional, Tuple

from talon import actions, app, settings

from .types import Data, Headers, Tool


def notify(message: str):
    """Send a notification to the user. Defaults the Andreas' notification system if you have it installed"""
    try:
        actions.user.notify(message)
    except:
        app.notify(message)
    # Log in case notifications are disabled
    print(message)


def generate_payload(
    prompt: str, content: str, tools: Optional[list[Tool]] = None
) -> Tuple[Headers, Data]:
    """Generate the headers and data for the OpenAI API GPT request.
    Does not return the URL given the fact not all openai-compatible endpoints support new features like tools
    """
    notify("GPT Task Started")

    try:
        TOKEN = os.environ["OPENAI_API_KEY"]
    except KeyError:
        message = "GPT Failure: env var OPENAI_API_KEY is not set."
        notify(message)
        raise Exception(message)

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

    data = {
        "messages": [
            {
                "role": "system",
                "content": settings.get("user.model_system_prompt")
                + additional_context,
            },
            {"role": "user", "content": f"{prompt}:\n{content}"},
        ],
        "max_tokens": 2024,
        "temperature": settings.get("user.model_temperature"),
        "n": 1,
        "stop": None,
        "model": settings.get("user.openai_model"),
    }

    if tools is not None:
        data["tools"] = tools

    return headers, data


def remove_wrapper(text: str):
    """Remove the string wrapper from the str representation of a command"""
    # different command wrapper for Linux.
    if platform.system() == "Linux":
        regex = r"^.*?'(.*?)'.*?$"
    else:
        # TODO condense these regexes. Hard to test between platforms
        # since the wrapper is slightly different
        regex = r'[^"]+"([^"]+)"'
    match = re.search(regex, text)
    return match.group(1) if match else text
