
from talon import Module, Context, ui

mod = Module()
ctx = Context()


mod.mode("NaturalMode", "Natural Speech AI Dictation Mode to intelligently correct text as it is typed")


@mod.action_class
class Actions:
    def gpt_process_natural(text: str):
        """Process text with natural speech AI"""
        window = ui.active_window()
        app = window.app
        title = window.title 

        ctx.settings["user.model_system_prompt"] = ""

