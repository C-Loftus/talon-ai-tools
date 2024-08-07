import os
from typing import Any

from talon import Module, actions, clip, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import (
    extract_message,
    format_clipboard,
    format_message,
    format_messages,
    messages_to_string,
    notify,
    send_request,
    thread_to_string,
)
from ..lib.modelState import GPTState

mod = Module()
mod.tag(
    "model_window_open",
    desc="Tag for enabling the model window commands when the window is open",
)


def gpt_query(prompt: dict[str, any], content: dict[str, any], destination: str = ""):
    """Send a prompt to the GPT API and return the response"""

    # Reset state before pasting
    GPTState.last_was_pasted = False

    response = send_request(prompt, content, None, destination)
    GPTState.last_response = extract_message(response)
    return response


@mod.action_class
class UserActions:
    def gpt_blend(source_text: str, destination_text: str):
        """Blend all the source text and send it to the destination"""
        prompt = f"""
        Act as a text transformer. I'm going to give you some source text and destination text, and I want you to modify the destination text based on the contents of the source text in a way that combines both of them together. Use the structure of the destination text, reordering and renaming as necessary to ensure a natural and coherent flow. Please return only the final text with no decoration for insertion into a document in the specified language.

        Here is the destination text:
        ```
        {destination_text}
        ```

        Please return only the final text. What follows is all of the source texts separated by '---'.
        """

        result = gpt_query(format_message(prompt), format_message(source_text))
        actions.user.gpt_insert_response(extract_message(result), "paste")

    def gpt_blend_list(source_text: list[str], destination_text: str):
        """Blend all the source text as a list and send it to the destination"""

        return actions.user.gpt_blend("\n---\n".join(source_text), destination_text)

    def gpt_generate_shell(text_to_process: str) -> str:
        """Generate a shell command from a spoken instruction"""
        shell_name = settings.get("user.model_shell_default")
        if shell_name is None:
            raise Exception("GPT Error: Shell name is not set. Set it in the settings.")

        prompt = f"""
        Generate a {shell_name} shell command that will perform the given task.
        Only include the code. Do not include any comments, backticks, or natural language explanations. Do not output the shell name, only the code that is valid {shell_name}.
        Condense the code into a single line such that it can be ran in the terminal.
        """

        result = gpt_query(format_message(prompt), format_message(text_to_process))
        return result.get("text", "")

    def gpt_generate_sql(text_to_process: str) -> str:
        """Generate a SQL query from a spoken instruction"""

        prompt = """
       Generate SQL to complete a given request.
       Output only the SQL in one line without newlines.
       Do not output comments, backticks, or natural language explanations.
       Prioritize SQL queries that are database agnostic.
        """
        return gpt_query(format_message(prompt), format_message(text_to_process)).get(
            "text", ""
        )

    def gpt_clear_context():
        """Reset the stored context"""
        GPTState.clear_context()

    def gpt_clear_thread():
        """Create a new thread"""
        GPTState.new_thread()

    def gpt_enable_threading():
        """Enable threading of subsequent requests"""
        GPTState.enable_thread()

    def gpt_disable_threading():
        """Enable threading of subsequent requests"""
        GPTState.disable_thread()

    def gpt_push_context(context: str):
        """Add the selected text to the stored context"""
        GPTState.push_context(format_message(context))

    def gpt_push_thread(content: str):
        """Add the selected text to the active thread"""
        GPTState.push_thread(format_messages("user", [format_message(content)]))

    def gpt_get_context():
        """Fetch the user context as a string"""
        return messages_to_string(GPTState.context)

    def gpt_get_thread():
        """Fetch the user thread as a string"""
        return thread_to_string(GPTState.thread)

    def contextual_user_context():
        """This is an override function that can be used to add additional context to the prompt"""
        return []

    def gpt_select_last():
        """select all the text in the last GPT output"""
        if not GPTState.last_was_pasted:
            notify("Tried to select GPT output, but it was not pasted in an editor")
            return

        lines = GPTState.last_response.split("\n")
        for _ in lines[:-1]:
            actions.edit.extend_up()
        actions.edit.extend_line_end()
        for _ in lines[0]:
            actions.edit.extend_left()

    def gpt_apply_prompt(prompt: str, source: str = "", destination: str = ""):
        """Apply an arbitrary prompt to arbitrary text"""
        response = actions.user.gpt_run_prompt(destination, prompt, source)
        actions.user.gpt_insert_response(response, destination)
        return response

    def gpt_run_prompt(destination: str, prompt: str, source: str) -> str:
        """Apply an arbitrary prompt to arbitrary text and return the response as text"""

        text_to_process = actions.user.gpt_get_source_text(source)

        # Handle special cases in the prompt
        ### Ask is a special case, where the text to process is the prompted question, not selected text
        if prompt.startswith("ask"):
            text_to_process = format_message(prompt.removeprefix("ask"))
            prompt = "Generate text that satisfies the question or request given in the input."

        # If the user is just moving the source to the destination, we don't need to apply a query
        if prompt == "pass":
            response = text_to_process
        else:
            response = gpt_query(format_message(prompt), text_to_process, destination)
        return extract_message(response)

    def gpt_help():
        """Open the GPT help file in the web browser"""
        # get the text from the file and open it in the web browser
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "lists", "staticPrompt.talon-list")
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

    def gpt_reformat_last(how_to_reformat: str):
        """Reformat the last model output"""
        PROMPT = f"""The last phrase was written using voice dictation. It has an error with spelling, grammar, or just general misrecognition due to a lack of context. Please reformat the following text to correct the error with the context that it was {how_to_reformat}."""
        last_output = actions.user.get_last_phrase()
        if last_output:
            actions.user.clear_last_phrase()
            return gpt_query(format_message(PROMPT), format_message(last_output))
        else:
            notify("No text to reformat")
            raise Exception("No text to reformat")

    def gpt_insert_response(
        result: str,
        method: str = "",
        cursorless_destination: Any = None,
    ):
        """Insert a GPT result in a specified way"""
        match method:
            case "above":
                actions.key("left")
                actions.edit.line_insert_up()
                GPTState.last_was_pasted = True
                actions.user.paste(result)
            case "below":
                actions.key("right")
                actions.edit.line_insert_down()
                GPTState.last_was_pasted = True
                actions.user.paste(result)
            case "clipboard":
                clip.set_text(result)
            case "snip":
                actions.user.insert_snippet(result)
            case "context":
                GPTState.push_context(format_message(result))
            case "newContext":
                GPTState.clear_context()
                GPTState.push_context(format_message(result))
            case "thread":
                GPTState.push_thread(format_messages("user", [format_message(result)]))
            case "newThread":
                GPTState.new_thread()
                GPTState.push_thread(format_messages("user", [format_message(result)]))
            case "appendClipboard":
                clip.set_text(clip.text() + "\n" + result)
            case "browser":
                builder = Builder()
                builder.h1("Talon GPT Result")
                for line in result.split("\n"):
                    builder.p(line)
                builder.render()
            case "textToSpeech":
                try:
                    actions.user.tts(result)
                except KeyError:
                    notify("GPT Failure: text to speech is not installed")

            # Although we can insert to a cursorless destination, the cursorless_target capture
            # Greatly increases DFA compliation times and should be avoided if possible
            case "cursorless":
                actions.user.cursorless_insert(cursorless_destination, result)
            case "window":
                actions.user.add_to_confirmation_gui(result)

            case "chain":
                GPTState.last_was_pasted = True
                actions.user.paste(result)
                actions.user.gpt_select_last()

            case "paste" | _:
                GPTState.last_was_pasted = True
                actions.user.paste(result)

    def gpt_get_source_text(spoken_text: str) -> dict[str, any]:
        """Get the source text that is will have the prompt applied to it"""
        match spoken_text:
            case "clipboard":
                return format_clipboard()
            case "context":
                return format_message(messages_to_string(GPTState.context))
            case "thread":
                return format_message(thread_to_string(GPTState.thread))
            case "gptResponse":
                if GPTState.last_response == "":
                    raise Exception(
                        "GPT Failure: User applied a prompt to the phrase GPT response, but there was no GPT response stored"
                    )
                return format_message(GPTState.last_response)

            case "lastTalonDictation":
                last_output = actions.user.get_last_phrase()
                if last_output:
                    actions.user.clear_last_phrase()
                    return format_message(last_output)
                else:
                    notify(
                        "GPT Failure: User applied a prompt to the phrase last Talon Dictation, but there was no text to reformat"
                    )
                    raise Exception(
                        "GPT Failure: User applied a prompt to the phrase last Talon Dictation, but there was no text to reformat"
                    )
            case "this" | _:
                return format_message(actions.edit.selected_text())
