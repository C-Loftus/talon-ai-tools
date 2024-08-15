from typing import ClassVar

from talon import actions

from .modelTypes import GPTMessage, GPTMessageItem


class GPTState:
    text_to_confirm: ClassVar[str] = ""
    last_response: ClassVar[str] = ""
    last_request: ClassVar[str] = ""
    last_was_pasted: ClassVar[bool] = False
    context: ClassVar[list[GPTMessageItem]] = []
    thread: ClassVar[list[GPTMessage]] = []
    thread_enabled: ClassVar[bool] = False

    @classmethod
    def clear_context(cls):
        """Reset the stored context"""
        cls.context = []
        actions.app.notify("Cleared user context")

    @classmethod
    def new_thread(cls):
        """Create a new thread"""
        cls.thread = []
        actions.app.notify("Created a new thread")

    @classmethod
    def enable_thread(cls):
        """Enable threading"""
        cls.thread_enabled = True
        actions.app.notify("Enabled threading")

    @classmethod
    def disable_thread(cls):
        """Disable threading"""
        cls.thread_enabled = False
        actions.app.notify("Disabled threading")

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
    def push_thread(cls, context: GPTMessage):
        """Add the selected text to the current thread"""
        cls.thread += [context]
        actions.app.notify("Appended to thread")

    @classmethod
    def reset_all(cls):
        cls.text_to_confirm = ""
        cls.last_response = ""
        cls.last_was_pasted = False
        cls.context = []
        cls.thread = []
