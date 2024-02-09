from talon import actions
from ..lib.HTMLbuilder import Builder
from typing import Callable
import inspect

# TODO Automatically generate tool schema from function signature 
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


function_specs = [
            {
                "type": "function",
                "function": {
                    "name": "insert",
                    "description": "Insert the string into the document. The document is in the language specified so if you aren't careful you will cause syntax errors.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The text to insert",
                            }
                        },
                        "required": ["str"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "notify",
                    "description": "Notify the user using a popup notification",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The text to notify",
                            }
                        },
                        "required": ["str"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "display",
                    "description": "DEFAULT - Display the response to the user. Use this for all informational text aside from notifications. Use this instead of returning content in the response.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The text to display",
                            }
                        },
                        "required": ["str"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_for_command",
                    "description": "Search for a command in the VSCode command palette. If I ask you to do something, please use this command to search for an appropriate command.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "The command to search for",
                            }
                        },
                        "required": ["str"],
                    },
                },
            }
]