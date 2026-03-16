"""Helper utilities for semantic step execution.

Purpose:
- Defines shared action call maps and runtime app/launch resolution helpers.

Called from:
- `GPT/semantic/gpt_semantic_step_executor.py`.
"""

try:
    from talon import ui as talon_ui
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    talon_ui = None

from .gpt_semantic_launch_catalog import resolve_launch_command

ARG_CALLS: dict[str, tuple[str | None, str, str]] = {
    "switch_app": ("user", "switcher_focus", "app_name"),
    "go_url": ("browser", "go", "url"),
    "find_text": ("edit", "find", "text"),
    "insert_text": (None, "insert", "text"),
    "key": (None, "key", "combo"),
}
NO_ARG_CALLS: dict[str, tuple[str, str]] = {
    "new_tab": ("app", "tab_open"),
    "copy": ("edit", "copy"),
    "paste": ("edit", "paste"),
    "select_all": ("edit", "select_all"),
    "undo": ("edit", "undo"),
    "redo": ("edit", "redo"),
    "line_start": ("edit", "line_start"),
    "line_end": ("edit", "line_end"),
    "delete_selection": ("edit", "delete"),
}


def is_running_app(app_name: str) -> bool:
    if talon_ui is None:
        return True
    target = _normalize_name(app_name)
    names = [
        _normalize_name(app.name) for app in talon_ui.apps(background=False) if app.name
    ]
    return any(name == target or target in name or name in target for name in names)


def validate_running_app(app_name: str) -> None:
    if is_running_app(app_name):
        return
    raise RuntimeError(f"App not running: '{app_name}'. Open it or use launch_app.")


def launch_candidates(app_name: str) -> list[str]:
    resolved = resolve_launch_command(app_name)
    return [resolved, app_name] if resolved and resolved != app_name else [app_name]


def _normalize_name(value: str) -> str:
    lowered = value.lower().replace("-", " ").replace("_", " ").strip()
    return " ".join(lowered.split())
