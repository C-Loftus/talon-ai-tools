from talon import Context, Module, actions, clip, imgui

from .modelHelpers import GPTState, notify

mod = Module()
ctx = Context()


@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()
    for line in GPTState.text_to_confirm.split("\n"):
        gui.text(line)

    gui.spacer()
    if gui.button("Paste response"):
        actions.user.paste_model_confirmation_gui()

    gui.spacer()
    if gui.button("Chain response"):
        actions.user.paste_model_confirmation_gui()
        actions.user.gpt_select_last()

    gui.spacer()
    if gui.button("Copy response"):
        actions.user.copy_model_confirmation_gui()

    gui.spacer()
    if gui.button("Discard response"):
        actions.user.close_model_confirmation_gui()


@mod.action_class
class UserActions:
    def add_to_confirmation_gui(model_output: str):
        """Add text to the confirmation gui"""
        ctx.tags = ["user.model_window_open"]
        GPTState.text_to_confirm = model_output
        confirmation_gui.show()

    def close_model_confirmation_gui():
        """Close the model output without pasting it"""
        GPTState.text_to_confirm = ""
        confirmation_gui.hide()
        ctx.tags = []

    def copy_model_confirmation_gui():
        """Copy the model output to the clipboard"""
        clip.set_text(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""

        actions.user.close_model_confirmation_gui()

    def paste_model_confirmation_gui():
        """Paste the model output"""
        if not GPTState.text_to_confirm:
            notify("GPT error: No text in confirmation GUI to paste")
            GPTState.text_to_confirm = ""
            actions.user.close_model_confirmation_gui()
            return
        else:
            actions.user.paste(GPTState.text_to_confirm)
            GPTState.last_response = GPTState.text_to_confirm
            GPTState.last_was_pasted = True
            GPTState.text_to_confirm = ""
            actions.user.close_model_confirmation_gui()
