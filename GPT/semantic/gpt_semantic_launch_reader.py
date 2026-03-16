"""Desktop entry reader for launchable app catalog.

Purpose:
- Scans .desktop files and extracts normalized executable launch entries.

Called from:
- `GPT/semantic/gpt_semantic_launch_catalog.py`.
"""

from configparser import ConfigParser
from pathlib import Path
from shlex import split
from shutil import which

LaunchEntries = tuple[tuple[str, str], ...]


class DesktopEntryReader:
    def __init__(self, directories: list[Path]):
        self.directories = directories

    def read_entries(self) -> LaunchEntries:
        merged: dict[str, str] = {}
        for file_path in self._desktop_files():
            parsed = self._parse_file(file_path)
            if parsed is not None:
                merged.setdefault(*parsed)
        return tuple(sorted(merged.items(), key=lambda item: item[0].lower()))

    def _desktop_files(self) -> list[Path]:
        files: list[Path] = []
        for directory in self.directories:
            if directory.exists():
                files.extend(directory.glob("*.desktop"))
        return files

    def _parse_file(self, file_path: Path) -> tuple[str, str] | None:
        parser = self._read_parser(file_path)
        if parser is None or not self._is_valid_entry(parser):
            return None
        return self._entry_values(parser)

    def _read_parser(self, file_path: Path) -> ConfigParser | None:
        parser = ConfigParser(interpolation=None, strict=False)
        try:
            parser.read(file_path, encoding="utf-8")
        except Exception:
            return None
        return parser

    def _is_valid_entry(self, parser: ConfigParser) -> bool:
        if parser.get("Desktop Entry", "Type", fallback="") != "Application":
            return False
        return (
            parser.get("Desktop Entry", "NoDisplay", fallback="false").lower() != "true"
        )

    def _entry_values(self, parser: ConfigParser) -> tuple[str, str] | None:
        name = parser.get("Desktop Entry", "Name", fallback="").strip()
        command = self._canonical_exec(
            self._clean_exec(parser.get("Desktop Entry", "Exec", fallback=""))
        )
        if not name or not command or self._looks_like_web_shortcut(name, command):
            return None
        return name, command

    def _clean_exec(self, exec_line: str) -> str:
        parts = [part for part in split(exec_line) if not part.startswith("%")]
        return " ".join(parts).strip()

    def _canonical_exec(self, command: str) -> str:
        parts = split(command) if command else []
        if not parts:
            return ""
        resolved = self._resolve_executable(parts[0])
        if resolved is None:
            return ""
        parts[0] = resolved
        return " ".join(parts)

    def _resolve_executable(self, command: str) -> str | None:
        if command.startswith("/") and Path(command).is_file():
            return command
        return which(command)

    def _looks_like_web_shortcut(self, name: str, command: str) -> bool:
        combined = f"{name}\n{command}".lower()
        return "http://" in combined or "https://" in combined
