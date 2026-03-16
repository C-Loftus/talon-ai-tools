"""Execution synchronization helpers for semantic steps.

Purpose:
- Waits for app focus after launch/switch and adds small settle delays between UI-sensitive steps.

Called from:
- `GPT/semantic/gpt_semantic_executor.py` during step execution.
"""

import time
from pathlib import Path
from shlex import split
from typing import Any

try:
    from talon import settings as talon_settings
    from talon import ui as talon_ui
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    talon_settings = None
    talon_ui = None

SETTLE_ACTIONS = {"launch_app", "switch_app", "new_tab", "focus_address", "go_url"}
POLL_INTERVAL_MS = 100


def wait_for_app_focus(runner: Any, app_name: str, command: str | None = None) -> None:
    timeout_ms = _int_setting("user.gpt_semantic_app_focus_timeout_ms", 3500)
    if talon_ui is None or timeout_ms <= 0:
        return
    hints = _focus_hints(app_name, command)
    deadline = time.monotonic() + (timeout_ms / 1000.0)
    while time.monotonic() < deadline:
        if _active_app_matches(hints):
            return
        runner.sleep(f"{POLL_INTERVAL_MS}ms")
    raise RuntimeError(f"App did not become active in {timeout_ms}ms: '{app_name}'")


def settle_after_step(action: str, runner: Any) -> None:
    if action not in SETTLE_ACTIONS:
        return
    delay_ms = _int_setting("user.gpt_semantic_step_settle_ms", 180)
    if delay_ms > 0:
        runner.sleep(f"{delay_ms}ms")


def _active_app_matches(hints: list[str]) -> bool:
    try:
        app = talon_ui.active_app() if talon_ui is not None else None
    except Exception:
        return False
    current = _normalize(app.name if app is not None else "")
    return any(_name_matches(current, hint) for hint in hints)


def _name_matches(current: str, hint: str) -> bool:
    return bool(
        current and hint and (current == hint or hint in current or current in hint)
    )


def _focus_hints(app_name: str, command: str | None) -> list[str]:
    values = [_normalize(app_name)]
    if command:
        values.extend(_command_hints(command))
    return [value for value in dict.fromkeys(values) if value]


def _command_hints(command: str) -> list[str]:
    executable = _first_token(command)
    name = Path(executable).stem if executable else ""
    return [_normalize(executable), _normalize(name)]


def _first_token(command: str) -> str:
    try:
        parts = split(command)
    except ValueError:
        return command.strip().split(" ")[0]
    return parts[0] if parts else ""


def _int_setting(name: str, default: int) -> int:
    if talon_settings is None:
        return 0
    try:
        value = talon_settings.get(name)
        return int(value) if value is not None else default
    except Exception:
        return default


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", " ").split())
