import textwrap

from talon import Context, Module, actions, clip, imgui, settings

from .modelHelpers import GPTState, notify

mod = Module()
ctx = Context()


@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()

    for paragraph in GPTState.text_to_confirm.split("\n"):
        for line in textwrap.wrap(
            paragraph, settings.get("user.model_window_char_width")
        ):
            gui.text(line)

    gui.spacer()
    if gui.button("Copy response"):
        actions.user.confirmation_gui_copy()

    gui.spacer()
    if gui.button("Paste response"):
        actions.user.confirmation_gui_paste()

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
        actions.user.confirmation_gui_close()

    def confirmation_gui_copy():
        """Copy the model output to the clipboard"""
        clip.set_text(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""

        actions.user.confirmation_gui_close()

    def confirmation_gui_paste():
        """Paste the model output"""

        if not GPTState.text_to_confirm:
            notify("GPT error: No text in confirmation GUI to paste")
        else:
            actions.user.paste(GPTState.text_to_confirm)
            GPTState.last_response = GPTState.text_to_confirm
            GPTState.last_was_pasted = True
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()
