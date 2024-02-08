from talon import actions
from ..lib.HTMLbuilder import Builder
from typing import Callable
import inspect

def _generate_tool(func: Callable):
    sig = inspect.signature(func)
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": inspect.getdoc(func),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }

    for name, param in sig.parameters.items():
        if param.default is param.empty:
            schema["function"]["parameters"]["required"].append(name)
        schema["function"]["parameters"]["properties"][name] = {
            "type": str(param.annotation).split("'")[1],
            "description": "",
        }

    return schema

def notify_user(response: str):
    """Send a notification to the desktop"""
    actions.app.notify(response)

def search_for_command(response: str):
    """Search VSCode for command"""
    actions.user.command_palette()
    actions.user.paste(response)

def display_response(response: str):
    """Open the GPT help file in the web browser"""
    builder = Builder()
    builder.h1("Displaying the Model Response")
    builder.p(response)
    builder.render()
