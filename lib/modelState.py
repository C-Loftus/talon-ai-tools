from typing import ClassVar

from talon import actions

from .modelTypes import GPTMessageItem


class GPTState:
    text_to_confirm: ClassVar[str] = ""
    last_response: ClassVar[str] = ""
    last_was_pasted: ClassVar[bool] = False
    context: ClassVar[list[GPTMessageItem]] = []
    debug_enabled: ClassVar[bool] = False

    @classmethod
    def start_debug(cls):
        """Enable debug printing"""
        GPTState.debug_enabled = True
        actions.app.notify("Enabled debug logging")

    @classmethod
    def stop_debug(cls):
        """Disable debug printing"""
        GPTState.debug_enabled = False
        actions.app.notify("Disabled debug logging")

    @classmethod
    def clear_context(cls):
        """Reset the stored context"""
        cls.context = []
        actions.app.notify("Cleared user context")

    @classmethod
    def push_context(cls, context: GPTMessageItem):
        """Add the selected text to the stored context"""
        if context.get("type") != "text":
            actions.app.notify(
                "Only text can be added to context. To add images, try using a prompt to summarize or otherwise describe the image to the context."
            )
            return
        cls.context += [context]
        actions.app.notify("Appended user context")

    @classmethod
    def reset_all(cls):
        cls.text_to_confirm = ""
        cls.last_response = ""
        cls.last_was_pasted = False
        cls.context = []
