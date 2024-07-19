from dataclasses import dataclass
from typing import Optional

from talon import Context, Module, actions, settings, ui

try:
    from talon.ui import Element
except ImportError:
    Element = type(None)
from talon.types import Span

ctx = Context()
ctx.matches = r"""
os: mac
app: code
"""

mod = Module()

# Default number of characters to use to acquire context. Somewhat arbitrary.
# The current dictation formatter doesn't need very many, but that could change in the future.
DEFAULT_CONTEXT_CHARACTERS = 30


@mod.action_class
class GenericActions:
    def a11y_get_full_editor_context() -> str:
        """Creates a `AccessibilityContext` representing the state of the document"""    
        return ""

@ctx.action_class('user')
class Actions:

    def a11y_get_full_editor_context() -> str:
        """Creates a `AccessibilityContext` representing the state of the document"""

        el = ui.focused_element()

        if not el.get("AXRoleDescription") == "editor":
            return ""

        if not el or not el.attrs:
            raise ValueError("No valid a11y element")

        context = el.get("AXValue")

        if context is None:
            raise ValueError("No accessibility information present")

        return context





