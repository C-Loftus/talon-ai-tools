# Adapted from MIT licensed code here:
# https://github.com/phillco/talon-axkit/blob/main/dictation/dictation_context.py

from talon import Context, Module, ui
from talon.types import Span

ctx = Context()
ctx.matches = r"""
os: mac
app: code
"""

mod = Module()


@mod.action_class
class GenericActions:
    def a11y_get_context_of_editor(selection: str) -> str:
        """Creates a `AccessibilityContext` representing the state of the document"""
        # If we aren't in a valid editor on a valid platform, just return an empty string
        return ""


@ctx.action_class("user")
class Actions:

    def a11y_get_context_of_editor(selection: str) -> str:
        """Creates a `AccessibilityContext` representing the state of the document"""

        el = ui.focused_element()

        if not el or not el.attrs:
            raise ValueError("No valid a11y element")

        # Only return extra context if we are in an editor
        if not el.get("AXRoleDescription") == "editor":
            return ""

        context = el.get("AXValue")

        if context is None:
            raise ValueError("No accessibility information present")
        # This probably means that a11y support is not enabled (we can't get more than just the current
        # selection)or that we selected the entire document
        if context == selection:
            return ""

        return context
