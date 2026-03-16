"""Launch entry provider that prefers community app_switcher data.

Purpose:
- Reuses community app switcher `get_apps()` for cross-platform launch discovery.
- Falls back to semantic desktop entry reader when community data is unavailable.

Called from:
- `GPT/semantic/gpt_semantic_launch_catalog.py`.
"""

from pathlib import Path
from typing import Callable

from .gpt_semantic_launch_reader import DesktopEntryReader

LaunchEntries = tuple[tuple[str, str], ...]


class LaunchProvider:
    def __init__(self, desktop_dirs: list[Path]):
        self.desktop_dirs = desktop_dirs

    def read_entries(self) -> LaunchEntries:
        return self._community_entries() or self._desktop_entries()

    def _community_entries(self) -> LaunchEntries:
        apps = self._load_community_apps()
        if not apps:
            return ()
        rows = sorted(apps.items(), key=lambda item: item[0].lower())
        return tuple(rows)

    def _desktop_entries(self) -> LaunchEntries:
        return DesktopEntryReader(self.desktop_dirs).read_entries()

    def _load_community_apps(self) -> dict[str, str]:
        getter = self._app_getter()
        if getter is None:
            return {}
        try:
            apps = getter()
        except Exception:
            return {}
        if not isinstance(apps, dict):
            return {}
        return {
            str(name): str(command)
            for name, command in apps.items()
            if str(name).strip() and str(command).strip()
        }

    def _app_getter(self) -> Callable[[], dict[str, str]] | None:
        module = self._import_switcher_module()
        getter = getattr(module, "get_apps", None) if module is not None else None
        return getter if callable(getter) else None

    def _import_switcher_module(self) -> object | None:
        names = [
            "user.community.core.app_switcher.app_switcher",
            "community.core.app_switcher.app_switcher",
        ]
        for name in names:
            try:
                module = __import__(name, fromlist=["get_apps"])
                return module
            except Exception:
                continue
        return None
