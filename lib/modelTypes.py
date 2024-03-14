import enum
from typing import Optional, TypedDict


class FunctionArguments(TypedDict):
    name: str
    arguments: str


class ToolCall(TypedDict):
    function: FunctionArguments


class Message(TypedDict):
    content: Optional[str]
    tool_calls: list[ToolCall]


class Choice(TypedDict):
    message: Message


class ChatCompletionResponse(TypedDict):
    choices: list[Choice]


class InsertOption(enum.Enum):
    PASTE = enum.auto()
    CURSORLESS = enum.auto()
    KEY_PRESSES = enum.auto()


Headers = dict[str, str]
Data = dict[str, str]
Tool = dict[str, str]
