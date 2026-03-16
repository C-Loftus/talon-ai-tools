import sys

sys.path.append(".")

from GPT.semantic.gpt_semantic_launch_provider import LaunchProvider


def test_read_entries_prefers_community(monkeypatch) -> None:
    provider = LaunchProvider([])
    monkeypatch.setattr(
        provider, "_community_entries", lambda: (("B", "2"), ("A", "1"))
    )
    monkeypatch.setattr(provider, "_desktop_entries", lambda: (("X", "x"),))
    assert provider.read_entries() == (("B", "2"), ("A", "1"))


def test_read_entries_falls_back_to_desktop(monkeypatch) -> None:
    provider = LaunchProvider([])
    monkeypatch.setattr(provider, "_community_entries", lambda: ())
    monkeypatch.setattr(provider, "_desktop_entries", lambda: (("X", "x"),))
    assert provider.read_entries() == (("X", "x"),)


def test_load_community_apps_filters_empty_values(monkeypatch) -> None:
    provider = LaunchProvider([])
    monkeypatch.setattr(
        provider,
        "_app_getter",
        lambda: lambda: {
            "Editor": "gedit",
            "": "bad",
            "Term": "",
            "Calc": "gnome-calculator",
        },
    )
    assert provider._load_community_apps() == {
        "Editor": "gedit",
        "Calc": "gnome-calculator",
    }
