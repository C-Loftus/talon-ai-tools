"""Planner context builder for semantic requests.

Purpose:
- Collects active window data, running apps, and launchable app catalog context.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py` during plan generation.
"""

from talon import actions

try:
    from talon import ui
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    ui = None

from .gpt_semantic_launch_catalog import launch_context_text


def semantic_context_text(request_text: str) -> str:
    return "\n\n".join(
        [_active_context(), _running_apps_context(), launch_context_text(request_text)]
    )


def _active_context() -> str:
    try:
        return actions.user.talon_get_active_context()
    except Exception:
        return f"Name: {actions.app.name()}\nTitle: {actions.win.title()}"


def _running_apps_context() -> str:
    names = _running_app_names()
    if names:
        return "Running apps for switch_app:\n" + ", ".join(names[:40])
    return "Running apps for switch_app: unavailable"


def _running_app_names() -> list[str]:
    if ui is None:
        return []
    return sorted({app.name for app in ui.apps(background=False) if app.name})
