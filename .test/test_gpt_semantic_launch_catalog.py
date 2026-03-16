import sys

sys.path.append(".")

from GPT.semantic import gpt_semantic_launch_catalog as catalog


def test_resolve_launch_command_prefers_name(monkeypatch) -> None:
    rows = (("Text Editor", "gnome-text-editor"), ("Terminal", "gnome-terminal"))
    monkeypatch.setattr(catalog, "launch_entries", lambda: rows)
    assert catalog.resolve_launch_command("text editor") == "gnome-text-editor"


def test_launch_context_text(monkeypatch) -> None:
    rows = (("Text Editor", "gnome-text-editor"),)
    monkeypatch.setattr(catalog, "launch_entries", lambda: rows)
    text = catalog.launch_context_text()
    assert "Launchable apps for launch_app" in text
    assert "Text Editor => gnome-text-editor" in text
