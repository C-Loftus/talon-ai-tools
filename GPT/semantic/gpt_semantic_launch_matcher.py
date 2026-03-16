"""Launch entry ranking and command resolution helpers.

Purpose:
- Resolves spoken app names to launch commands.
- Ranks launch catalog entries by request relevance.

Called from:
- `GPT/semantic/gpt_semantic_launch_catalog.py`.
"""

from .gpt_semantic_launch_text import command_name, normalize_text

LaunchEntries = tuple[tuple[str, str], ...]


class LaunchMatcher:
    def __init__(self, stop_words: set[str]):
        self.stop_words = stop_words

    def resolve(self, app_name: str, entries: LaunchEntries) -> str | None:
        target = normalize_text(app_name)
        return self._resolve_name(target, entries) or self._resolve_command(
            target, entries
        )

    def rank_entries(
        self, query: str, entries: LaunchEntries, limit: int
    ) -> list[tuple[str, str]]:
        if not query.strip():
            return list(entries[:limit])
        return self._rank_with_query(query, entries, limit)

    def _resolve_name(self, target: str, entries: LaunchEntries) -> str | None:
        for name, command in entries:
            if normalize_text(name) == target or (
                target and target in normalize_text(name)
            ):
                return command
        return None

    def _resolve_command(self, target: str, entries: LaunchEntries) -> str | None:
        for _, command in entries:
            if command_name(command) == target:
                return command
        return None

    def _rank_with_query(
        self, query: str, entries: LaunchEntries, limit: int
    ) -> list[tuple[str, str]]:
        scored = [(*row, self._score(query, *row)) for row in entries]
        scored.sort(key=lambda row: (-row[2], row[0].lower()))
        return [(name, command) for name, command, _ in scored[:limit]]

    def _score(self, query: str, name: str, command: str) -> int:
        target = normalize_text(query)
        if not target:
            return 0
        name_key = normalize_text(name)
        command_key = command_name(command)
        score = self._base_score(target, name_key, command_key)
        return score + self._token_score(target, name_key, command_key)

    def _base_score(self, target: str, name_key: str, command_key: str) -> int:
        if target == name_key or target == command_key:
            return 10
        if target in name_key or target in command_key:
            return 5
        return 0

    def _token_score(self, target: str, name_key: str, command_key: str) -> int:
        tokens = [
            token
            for token in target.split()
            if token not in self.stop_words and len(token) > 1
        ]
        return sum(1 for token in tokens if token in name_key or token in command_key)
