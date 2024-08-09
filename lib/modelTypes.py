from typing import Literal, NotRequired, TypedDict


class GPTMessageItem(TypedDict):
    type: Literal["text", "image_url"]
    text: NotRequired[str]
    image_url: NotRequired[dict[Literal["url"], str]]


class GPTMessage(TypedDict):
    role: Literal["user", "system", "assistant"]
    content: list[GPTMessageItem]
