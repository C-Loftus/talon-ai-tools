import inspect
from typing import Callable

from talon import actions

from ...lib.HTMLBuilder import Builder

"""
To create a new function callable by the GPT model, create a new function and add its serialization to the function_specs list.
"""
# TODO make it automatically called in the match statement in gpt-function-calling.py Might require scary eval stuff


def _to_openai_type(arg: str):
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

    def __init__(self, function: Callable, *arg_descriptions: str):
        """
        Create a new callable function for the GPT model by providing a function and a list of argument descriptions. The argument descriptions should be in the same order as the function's arguments. The docstring and argument names are used to generate the function's description and argument names.
        """
        self.function = function
        description = inspect.getdoc(function)

        if description is None:
            raise ValueError("The function must have a docstring")

        self.description = description

        # get list of argumment names and types
        arg_names = list(inspect.signature(function).parameters.keys())

        arg_types = [
            _to_openai_type(arg.annotation.__name__)
            for arg in inspect.signature(function).parameters.values()
        ]

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
    """Notify the user a message using a popup notification"""
    actions.app.notify(response)


def search_for_command(response: str):
    """Search VSCode for command"""
    actions.user.command_palette()
    actions.user.paste(response)


def display_response(response: str):
    """Display the response to the user in a new window."""
    builder = Builder()
    builder.h1("Displaying the Model Response")
    builder.p(response)
    builder.render()


def insert_response(response: str):
    """Insert or type the result of a user request into the current document, replacing or generating text."""
    actions.user.paste(response)


# This is the list of functions that can be called by the GPT model
function_specs = [
    CallableFunction(display_response, "The text to display").serialize(),
    CallableFunction(notify_user, "The text to notify").serialize(),
    CallableFunction(search_for_command, "The command to search for").serialize(),
    CallableFunction(insert_response, "The text to insert").serialize(),
]
