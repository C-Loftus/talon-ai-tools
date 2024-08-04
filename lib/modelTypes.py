import enum
from typing import Literal, Optional, TypedDict


class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class GPTMessage:
    type: Literal["text", "image_url"]
    content: str

    def __init__(self, content: str, type: Literal["text", "image_url"] = "text"):
        self.content = content
        self.type = type

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content,
        }

    def get_content(self):
        return self.content


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
