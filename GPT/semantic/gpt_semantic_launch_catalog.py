"""Launchable app catalog utilities for semantic `launch_app`.

Purpose:
- Provides public launch catalog APIs used by planner context and executor.
- Delegates reading and matching to focused helper modules.

Called from:
- `GPT/semantic/gpt_semantic_context.py` to build planner context.
- `GPT/semantic/gpt_semantic_executor_helpers.py` to resolve launch commands.
"""

from functools import lru_cache
from pathlib import Path

from .gpt_semantic_launch_matcher import LaunchMatcher
from .gpt_semantic_launch_provider import LaunchProvider

DESKTOP_DIRS = [
    Path.home() / ".local/share/applications",
    Path("/usr/share/applications"),
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local/share/flatpak/exports/share/applications",
]
STOP_WORDS = {
    "a",
    "an",
    "app",
    "application",
    "launch",
    "model",
    "open",
    "please",
    "run",
    "start",
    "the",
}


def launch_context_text(query: str = "", limit: int = 300) -> str:
    entries = _matcher().rank_entries(query, launch_entries(), limit)
    if not entries:
        return "Launchable apps for launch_app: unavailable"
    lines = ["Launchable apps for launch_app (name => command):"]
    lines.extend(f"- {name} => {command}" for name, command in entries)
    return "\n".join(lines)


def resolve_launch_command(app_name: str) -> str | None:
    return _matcher().resolve(app_name, launch_entries())


@lru_cache(maxsize=1)
def launch_entries() -> tuple[tuple[str, str], ...]:
    return LaunchProvider(DESKTOP_DIRS).read_entries()


def _matcher() -> LaunchMatcher:
    return LaunchMatcher(STOP_WORDS)
