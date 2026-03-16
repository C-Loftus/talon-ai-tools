"""Browser action compatibility helpers for semantic steps.

Purpose:
- Wraps browser actions and provides key-based fallbacks when browser modules are missing.

Called from:
- `GPT/semantic/gpt_semantic_executor.py`
"""

from typing import Any


def call_go_url(runner: Any, url: str) -> None:
    try:
        runner.browser.go(url)
    except Exception as exc:
        if not _is_missing_action(exc, "browser.go"):
            raise
        runner.key("ctrl-l")
        runner.insert(url)
        runner.key("enter")


def call_focus_address(runner: Any) -> None:
    try:
        runner.browser.focus_address()
    except Exception as exc:
        if not _is_missing_action(exc, "browser.focus_address"):
            raise
        runner.key("ctrl-l")


def _is_missing_action(exc: Exception, action_name: str) -> bool:
    message = str(exc).lower()
    if action_name not in message:
        return False
    return (
        "module method is empty" in message or "no context reimplements it" in message
    )
