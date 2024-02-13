import inspect
from typing import Callable

from talon import actions

from ..lib.HTMLbuilder import Builder

"""
To create a new function callable by the GPT model, create a new function and add its serialization to the function_specs list.
"""
# TODO make it automatically called in the match statement in gpt-function-calling.py Might require scary eval stuff


def _to_openai_type(arg):
    match arg:
        case "str":
            return "string"
        case "int":
            return "integer"
        case "bool":
            return "boolean"
        case _:
            raise ValueError(f"Unsupported type: {arg}")


# Currently only supports mandatory arguments
class CallableFunction:
    # The function to call
    function: Callable
    # The description of the function
    description: str
    # List of arg name, arg type, arg description
    args: list[tuple[str, str, str]]

    def __init__(self, function: Callable, arg_descriptions: list[str] | str | None):
        """
        Create a new callable function for the GPT model by providing a function and a list of argument descriptions. The argument descriptions should be in the same order as the function's arguments. The docstring and argument names are used to generate the function's description and argument names.
        """
        self.function = function
        self.description = inspect.getdoc(function)

        # get list of argumment names and types
        arg_names = list(inspect.signature(function).parameters.keys())
        arg_names = [str(arg) for arg in arg_names]

        arg_types = list(inspect.signature(function).parameters.values())
        arg_types = [str(arg).split(":")[1].strip() for arg in arg_types]
        arg_types = [_to_openai_type(arg) for arg in arg_types]

        # Convert arg_descriptions to a list if it is a string to make it length-wise comparable
        if isinstance(arg_descriptions, str):
            arg_descriptions = [arg_descriptions]

        # Make sure there are descriptions for all arguments
        if len(arg_descriptions) != len(arg_names):
            raise ValueError(
                "The number of descriptions must match the number of arguments"
            )

        self.args = list(zip(arg_names, arg_types, arg_descriptions))

    def serialize(self):
        properties = {
            arg_name: {"type": arg_type, "description": arg_description}
            for (arg_name, arg_type, arg_description) in self.args
        }

        return {
            "type": "function",
            "function": {
                "name": self.function.__name__,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": [arg_name for arg_name, _, _ in self.args],
                },
            },
        }


def notify_user(response: str):
    """Notify the user using a popup notification"""
    actions.app.notify(response)


def search_for_command(response: str):
    """Search VSCode for command"""
    actions.user.command_palette()
    actions.user.paste(response)


def display_response(response: str):
    """Display the response to the user. Use this for all informational text aside from notifications. Use this instead of returning content in the response."""
    builder = Builder()
    builder.h1("Displaying the Model Response")
    builder.p(response)
    builder.render()


def insert_response(response: str):
    """Insert the response into the current document using proper syntax for the current language. This is the default action if no other function is found."""
    actions.user.paste(response)


# This is the list of functions that can be called by the GPT model
function_specs = [
    CallableFunction(display_response, "The text to display").serialize(),
    CallableFunction(notify_user, "The text to notify").serialize(),
    CallableFunction(search_for_command, "The command to search for").serialize(),
]
