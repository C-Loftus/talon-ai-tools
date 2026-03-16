"""Text normalization helpers for semantic launch catalog logic.

Purpose:
- Normalizes app names and commands for matching and ranking.

Called from:
- `GPT/semantic/gpt_semantic_launch_matcher.py`
- `GPT/semantic/gpt_semantic_launch_reader.py`
"""

from shlex import split


def normalize_text(value: str) -> str:
    words = value.strip().lower().replace("-", " ").split()
    return " ".join(words)


def first_token(command: str) -> str:
    if not command:
        return ""
    return _split_parts(command)[0]


def command_name(command: str) -> str:
    return normalize_text(first_token(command))


def _split_parts(command: str) -> list[str]:
    try:
        parts = split(command)
    except ValueError:
        parts = command.strip().split()
    return parts if parts else [""]
