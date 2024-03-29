from talon import Context, Module, actions, ui

mod = Module()
accessAPIPlatforms = Context()

accessAPIPlatforms.matches = r"""
os: mac
os: windows
"""

# Can't use accessibility APIs on linux
# so we just use the raw dictation output
bareDictationCtx = Context()

bareDictationCtx.matches = r"""
os: linux
"""


@mod.action_class
class Actions:
    def gpt_dictation_insert(text: str):
        """Process text with natural speech AI"""


@accessAPIPlatforms.action_class("user")
class WindowsActions:
    def gpt_dictation_insert(text: str):
        """Process text with natural speech AI"""
        window = ui.active_window()
        app = window.app
        title = window.title
        # current_text_box = ui.focused_element().text_pattern.selection[0].get_text(400)

        # TODO figure out length so system prompt is not too long
        current_text_box = ui.focused_element().text_pattern.document_range.get_text(
            1000
        )

        system_prompt = f"""The user is dictating voice dictation and there may be errors or missing puncuation and style. The currently focused application is {app} and the window title is {title}. That may or may not be relevant. Try to infer the proper text and style fixes to insert. The text so far include the following text in quotes: '{current_text_box}'"""

        accessAPIPlatforms.settings["user.model_system_prompt"] = system_prompt

        prompt = "Return the same text but fix any misrecognitions or mistakes in puncutation due to voice dictation."
        response = actions.user.gpt_apply_prompt(prompt, text)
        actions.insert(response)


@bareDictationCtx.action_class("user")
class LinuxActions:
    def gpt_dictation_insert(text: str):
        """Process text with natural speech AI"""
