import base64
import json
import logging
import os
import platform
import subprocess
from typing import Literal, Optional

import requests
from talon import actions, app, clip, settings

from ..lib.pureHelpers import strip_markdown
from .modelState import GPTState
from .modelTypes import GPTMessage, GPTMessageItem

""""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""


def resolve_model_name(model: str) -> str:
    """
    Get the actual model name from the model list value.
    """
    if model == "model":
        # Check for deprecated setting first for backward compatibility
        openai_model: str = settings.get("user.openai_model")  # type: ignore
        if openai_model != "do_not_use":
            logging.warning(
                "The setting 'user.openai_model' is deprecated. Please use 'user.model_default' instead."
            )
            model = openai_model
        else:
            model = settings.get("user.model_default")  # type: ignore
    return model


def messages_to_string(messages: list[GPTMessageItem]) -> str:
    """Format messages as a string"""
    formatted_messages = []
    for message in messages:
        if message.get("type") == "image_url":
            formatted_messages.append("image")
        else:
            formatted_messages.append(message.get("text", ""))
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
    model: str,
    thread: str,
    destination: str = "",
) -> GPTMessageItem:
    """Generate run a GPT request and return the response"""
    model = resolve_model_name(model)

    continue_thread = thread == "continueLast"

    notification = "GPT Task Started"
    if len(GPTState.context) > 0:
        notification += ": Reusing Stored Context"

    # Use specified model if provided
    if model:
        notification += f", Using model: {model}"

    if settings.get("user.model_verbose_notifications"):
        notify(notification)

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

    system_message = "\n\n".join(
        [
            item
            for item in [
                settings.get("user.model_system_prompt"),
                language_context,
                application_context,
                snippet_context,
            ]
            + actions.user.gpt_additional_user_context()
            + [context.get("text") for context in GPTState.context]
            if item
        ]
    )

    content: list[GPTMessageItem] = [prompt]
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
            content = [prompt]

    request = GPTMessage(
        role="user",
        content=content,
    )

    model_endpoint: str = settings.get("user.model_endpoint")  # type: ignore
    if model_endpoint == "llm":
        response = send_request_to_llm_cli(
            prompt, content_to_process, system_message, model, continue_thread
        )
    else:
        if continue_thread:
            notify(
                "Warning: Thread continuation is only supported when using setting user.model_endpoint = 'llm'"
            )
        response = send_request_to_api(request, system_message, model)

    return response


def send_request_to_api(
    request: GPTMessage, system_message: str, model: str
) -> GPTMessageItem:
    """Send a request to the model API endpoint and return the response"""
    data = {
        "messages": (
            [
                format_messages(
                    "system",
                    [GPTMessageItem(type="text", text=system_message)],
                ),
            ]
            if system_message
            else []
        )
        + [request],
        "max_tokens": 2024,
        "temperature": settings.get("user.model_temperature"),
        "n": 1,
        "model": model,
    }
    if GPTState.debug_enabled:
        print(data)

    url: str = settings.get("user.model_endpoint")  # type: ignore
    headers = {"Content-Type": "application/json"}
    token = get_token()
    # If the model endpoint is Azure, we need to use a different header
    if "azure.com" in url:
        headers["api-key"] = token
    else:
        headers["Authorization"] = f"Bearer {token}"

    raw_response = requests.post(url, headers=headers, data=json.dumps(data))

    match raw_response.status_code:
        case 200:
            if settings.get("user.model_verbose_notifications"):
                notify("GPT Task Completed")
            resp = raw_response.json()["choices"][0]["message"]["content"].strip()
            formatted_resp = strip_markdown(resp)
            return format_message(formatted_resp)
        case _:
            notify("GPT Failure: Check the Talon Log")
            raise Exception(raw_response.json())


def send_request_to_llm_cli(
    prompt: GPTMessageItem,
    content_to_process: Optional[GPTMessageItem],
    system_message: str,
    model: str,
    continue_thread: bool,
) -> GPTMessageItem:
    """Send a request to the LLM CLI tool and return the response"""
    # Build command.
    command: list[str] = [settings.get("user.model_llm_path")]  # type: ignore
    if continue_thread:
        command.append("-c")
    command.append(prompt["text"])  # type: ignore
    cmd_input: bytes | None = None
    if content_to_process and content_to_process["type"] == "image_url":
        img_url: str = content_to_process["image_url"]["url"]  # type: ignore
        if img_url.startswith("data:"):
            command.extend(["-a", "-"])
            base64_data: str = img_url.split(",", 1)[1]
            cmd_input = base64.b64decode(base64_data)
        else:
            command.extend(["-a", img_url])
    command.extend(["-m", model])
    command.extend(["-o", "temperature", str(settings.get("user.model_temperature"))])
    if system_message:
        command.extend(["-s", system_message])

    if GPTState.debug_enabled:
        print(command)

    # Execute command and capture output.
    # Talon changes locale.getpreferredencoding(False) to "utf-8" on
    # Windows, but the llm command responds with cp1252 encoding.
    output_encoding = "cp1252" if platform.system() == "Windows" else "utf-8"
    try:
        result = subprocess.run(
            command,
            input=cmd_input,
            capture_output=True,
            check=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            ),
        )
        if settings.get("user.model_verbose_notifications"):
            notify("GPT Task Completed")
        resp = result.stdout.decode(output_encoding).strip()
        formatted_resp = strip_markdown(resp)
        return format_message(formatted_resp)
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode(output_encoding).strip() if e.stderr else str(e)
        notify(f"GPT Failure: {error_msg}")
        raise e
    except Exception as e:
        notify("GPT Failure: Check the Talon Log")
        raise e


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
