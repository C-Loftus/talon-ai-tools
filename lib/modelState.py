from talon import actions
from typing import ClassVar


class GPTState:
    text_to_confirm: ClassVar[str] = ""
    last_response: ClassVar[str] = ""
    last_was_pasted: ClassVar[bool] = False
    context: ClassVar[list] = []
    thread: ClassVar[list] = []

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
    def push_context(cls, context: dict[str, any]):
        """Add the selected text to the stored context"""
        cls.context += [context]
        actions.app.notify("Appended user context")

    @classmethod
    def push_thread(cls, context: dict[str, any]):
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
