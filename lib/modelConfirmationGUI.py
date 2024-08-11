from typing import Optional
from talon import Context, Module, actions, clip, imgui

from .modelHelpers import GPTState, extract_message, notify

mod = Module()
ctx = Context()


@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()

    # This is a heuristic. realistically, it is extremely unlikely that
    # any other text would have both of these literals in the text
    # to confirm and it not represent a thread
    display_thread: bool = (
        "USER" in GPTState.text_to_confirm and "GPT" in GPTState.text_to_confirm
    )

    last_message_item = GPTState.thread[-1]["content"][0]
    last_item_text = last_message_item.get("text", None)

    for line in GPTState.text_to_confirm.split("\n"):
        gui.text(line)

    # gui.spacer()
    # if gui.button("Chain response"):
    #     actions.user.confirmation_gui_paste()
    #     actions.user.gpt_select_last()

    # gui.spacer()
    # if gui.button("Pass response to context"):
    #     actions.user.confirmation_gui_pass_context()

    # gui.spacer()
    # if gui.button("Pass response to thread"):
    #     actions.user.confirmation_gui_pass_thread()

    gui.spacer()
    if gui.button("Copy response"):
        if display_thread:
            actions.user.confirmation_gui_copy()
        else:
            actions.user.confirmation_gui_copy(last_item_text)

    gui.spacer()
    if gui.button("Paste response"):
        if display_thread:
            actions.user.confirmation_gui_paste()
        else:
            actions.user.confirmation_gui_paste(last_item_text)

    gui.spacer()
    if gui.button("Discard response"):
        actions.user.confirmation_gui_close()


@mod.action_class
class UserActions:
    def confirmation_gui_append(model_output: str):
        """Add text to the confirmation gui"""
        ctx.tags = ["user.model_window_open"]
        GPTState.text_to_confirm = model_output
        confirmation_gui.show()

    def confirmation_gui_close():
        """Close the model output without pasting it"""
        GPTState.text_to_confirm = ""
        confirmation_gui.hide()
        ctx.tags = []

    def confirmation_gui_pass_context():
        """Add the model output to the context"""
        actions.user.gpt_push_context(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.close_model_confirmation_gui()

    def confirmation_gui_pass_thread():
        """Add the model output to the thread"""

        actions.user.gpt_push_thread(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.close_model_confirmation_gui()

    def confirmation_gui_copy(string_override: Optional[str] = None):
        """Copy the model output to the clipboard"""
        text_to_set = (
            GPTState.text_to_confirm if not string_override else string_override
        )

        clip.set_text(text_to_set)
        GPTState.text_to_confirm = ""

        actions.user.close_model_confirmation_gui()

    def confirmation_gui_paste(string_override: Optional[str] = None):
        """Paste the model output"""
        text_to_set = (
            GPTState.text_to_confirm if not string_override else string_override
        )

        if not text_to_set:
            notify("GPT error: No text in confirmation GUI to paste")
        else:
            actions.user.paste(text_to_set)
            GPTState.last_response = text_to_set
            GPTState.last_was_pasted = True
        GPTState.text_to_confirm = ""
        actions.user.close_model_confirmation_gui()

    def confirmation_gui_refresh_thread(force_open: bool = False):
        """Refresh the threading output in the confirmation GUI"""

        formatted_output = ""
        for msg in GPTState.thread:
            for item in msg["content"]:
                role = "GPT" if msg["role"] == "assistant" else "USER"
                output = f"{role}: {extract_message(item)}"
                # every 100 characters split the output into multiple lines
                formatted_output += (
                    "\n".join(output[i : i + 100] for i in range(0, len(output), 100))
                    + "\n"
                )

        GPTState.text_to_confirm = formatted_output
        ctx.tags = ["user.model_window_open"]
        if confirmation_gui.showing or force_open:
            confirmation_gui.show()
