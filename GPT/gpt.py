import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, ClassVar, Literal

import requests
from talon import Module, actions, clip, imgui, registry, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import generate_payload, notify, remove_wrapper

mod = Module()


class GuiState:
    text_to_confirm: ClassVar[str] = ""


@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()
    gui.text(GuiState.text_to_confirm)

    gui.spacer()
    if gui.button("Paste model output"):
        actions.user.paste_model_confirmation_gui()

    gui.spacer()
    if gui.button("Copy model output"):
        actions.user.copy_model_confirmation_gui()

    gui.spacer()
    if gui.button("Deny model output"):
        actions.user.close_model_confirmation_gui()


def gpt_query(prompt: str, content: str) -> str:
    url = settings.get("user.model_endpoint")

    headers, data = generate_payload(prompt, content)

    response = requests.post(url, headers=headers, data=json.dumps(data))

    match response.status_code:
        case 200:
            notify("GPT Task Completed")
            return response.json()["choices"][0]["message"]["content"].strip()
        case _:
            notify("GPT Failure: Check the Talon Log")
            raise Exception(response.json())


@mod.action_class
class UserActions:
    def gpt_answer_question(text_to_process: str) -> str:
        """Answer an arbitrary question"""
        prompt = """
        Generate text that satisfies the question or request given in the input.
        """
        return gpt_query(prompt, text_to_process)

    def gpt_generate_shell(text_to_process: str) -> str:
        """Generate a shell command from a spoken instruction"""
        shell_name = settings.get("user.model_shell_default")
        if shell_name == None:
            raise Exception("GPT Error: Shell name is not set. Set it in the settings.")

        prompt = f"""
        Generate a {shell_name} shell command that will perform the given task.
        Only include the code. Do not include any comments, backticks, or natural language explanations. Do not output the shell name, only the code that is valid {shell_name}.
        Condense the code into a single line such that it can be ran in the terminal.
        """

        result = gpt_query(prompt, text_to_process)
        return result

    def gpt_generate_sql(text_to_process: str) -> str:
        """Generate a SQL query from a spoken instruction"""

        prompt = """
       Generate SQL to complete a given request.
       Output only the SQL in one line without newlines.
       Do not output comments, backticks, or natural language explanations.
       Prioritize SQL queries that are database agnostic.
        """
        return gpt_query(prompt, text_to_process)

    def add_to_confirmation_gui(model_output: str):
        """Add text to the confirmation gui"""
        GuiState.text_to_confirm = model_output
        confirmation_gui.show()

    def close_model_confirmation_gui():
        """Close the model output without pasting it"""
        GuiState.text_to_confirm = ""
        confirmation_gui.hide()

    def copy_model_confirmation_gui():
        """Copy the model output to the clipboard"""
        clip.set_text(GuiState.text_to_confirm)
        GuiState.text_to_confirm = ""

        confirmation_gui.hide()

    def paste_model_confirmation_gui():
        """Paste the model output"""
        actions.user.paste(GuiState.text_to_confirm)
        GuiState.text_to_confirm = ""
        confirmation_gui.hide()

    def paste_and_select(result: str):
        """Paste and select the pasted text"""

        actions.user.paste(result)

        for _ in result:
            actions.edit.extend_left()

    def gpt_apply_prompt(prompt: str, text_to_process: str | list[str]) -> str:
        """Apply an arbitrary prompt to arbitrary text"""
        text_to_process = (
            " ".join(text_to_process)
            if isinstance(text_to_process, list)
            else text_to_process
        )
        return gpt_query(prompt, text_to_process)

    def gpt_help():
        """Open the GPT help file in the web browser"""
        # get the text from the file and open it in the web browser
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "staticPrompt.talon-list")
        with open(file_path, "r") as f:
            lines = f.readlines()[2:]

        builder = Builder()
        builder.h1("Talon GPT Prompt List")
        for line in lines:
            if "##" in line:
                builder.h2(line)
            else:
                builder.p(line)

        builder.render()

    def gpt_find_talon_commands(command_description: str):
        """Search for relevant talon commands"""
        command_list = ""
        for ctx in registry.active_contexts():
            items = ctx.commands.items()
            for _, command in items:
                raw_command = remove_wrapper(str(command))
                delimited = f"{raw_command}\n"
                command_list += delimited

        prompt = f"""
        The following is a list of commands separated by \n for a program that controls the user's desktop. Each command after the delimiter is a separate command unrelated to the previous command.
        I am a user and I want to find {command_description}.
        Return the exact relevant command or the exact word "None" and nothing else.
        """

        # TODO: tokenize instead of splitting by character
        def split_into_chunks(text: str, chunk_size: int):
            return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

        command_chunks = split_into_chunks(command_list, 1400 - len(prompt))

        with ThreadPoolExecutor() as executor:
            results = list(
                executor.map(gpt_query, [prompt] * len(command_chunks), command_chunks)
            )

        builder = Builder()
        builder.h1("Talon GPT Command Response")
        for result in results:
            if result != "None":
                builder.p(result)
        builder.render()

    def gpt_reformat_last(how_to_reformat: str):
        """Reformat the last model output"""
        PROMPT = f"""The last phrase was written using voice dictation. It has an error with spelling, grammar, or just general misrecognition due to a lack of context. Please reformat the following text to correct the error with the context that it was {how_to_reformat}."""
        last_output = actions.user.get_last_phrase()
        if last_output:
            actions.user.clear_last_phrase()
            return gpt_query(PROMPT, last_output)
        else:
            notify("No text to reformat")
            raise Exception("No text to reformat")

    def cursorless_or_paste_helper(
        cursorless_destination: Any | Literal[0], text: str
    ) -> None:
        """If a destination is specified, use cursorless to insert text. Otherwise, paste the text."""
        if cursorless_destination == 0:
            actions.user.paste(text)
        else:
            actions.user.cursorless_insert(cursorless_destination, text)
