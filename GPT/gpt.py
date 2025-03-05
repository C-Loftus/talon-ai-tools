import logging
import os
from typing import Any, Optional

from talon import Module, actions, clip, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelConfirmationGUI import confirmation_gui
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
from ..lib.modelTypes import GPTMessageItem

mod = Module()
mod.tag(
    "model_window_open",
    desc="Tag for enabling the model window commands when the window is open",
)


def gpt_query(
    prompt: GPTMessageItem,
    text_to_process: Optional[GPTMessageItem],
    model: str,
    destination: str = "",
):
    """Send a prompt to the GPT API and return the response"""

    # Reset state before pasting
    GPTState.last_was_pasted = False

    response = send_request(prompt, text_to_process, model, destination)
    GPTState.last_response = extract_message(response)
    return response


@mod.action_class
class UserActions:
    def gpt_blend(source_text: str, destination_text: str, model: str) -> None:
        """Blend all the source text and send it to the destination"""
        prompt = f"""
        Act as a text transformer. I'm going to give you some source text and destination text, and I want you to modify the destination text based on the contents of the source text in a way that combines both of them together. Use the structure of the destination text, reordering and renaming as necessary to ensure a natural and coherent flow. Please return only the final text with no decoration for insertion into a document in the specified language.

        Here is the destination text:
        ```
        {destination_text}
        ```

        Please return only the final text. What follows is all of the source texts separated by '---'.
        """

        result = gpt_query(format_message(prompt), format_message(source_text), model)
        actions.user.gpt_insert_response(result, "paste")

    def gpt_blend_list(
        source_text: list[str], destination_text: str, model: str
    ) -> None:
        """Blend all the source text as a list and send it to the destination"""

        return actions.user.gpt_blend(
            "\n---\n".join(source_text), destination_text, model
        )

    def gpt_generate_shell(text_to_process: str, model: str) -> str:
        """Generate a shell command from a spoken instruction"""
        shell_name = settings.get("user.model_shell_default")
        if shell_name is None:
            raise Exception("GPT Error: Shell name is not set. Set it in the settings.")

        prompt = f"""
        Generate a {shell_name} shell command that will perform the given task.
        Only include the code. Do not include any comments, backticks, or natural language explanations. Do not output the shell name, only the code that is valid {shell_name}.
        Condense the code into a single line such that it can be ran in the terminal.
        """

        result = gpt_query(
            format_message(prompt), format_message(text_to_process), model
        )
        return extract_message(result)

    def gpt_generate_sql(text_to_process: str, model: str) -> str:
        """Generate a SQL query from a spoken instruction"""

        prompt = """
       Generate SQL to complete a given request.
       Output only the SQL in one line without newlines.
       Do not output comments, backticks, or natural language explanations.
       Prioritize SQL queries that are database agnostic.
        """
        return gpt_query(
            format_message(prompt), format_message(text_to_process), model
        ).get("text", "")

    def gpt_start_debug():
        """Enable debug logging"""
        GPTState.start_debug()

    def gpt_stop_debug():
        """Disable debug logging"""
        GPTState.stop_debug()

    def gpt_clear_context():
        """Reset the stored context"""
        GPTState.clear_context()

    def gpt_clear_thread():
        """Create a new thread"""
        GPTState.new_thread()
        actions.user.confirmation_gui_refresh_thread()

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

    def gpt_additional_user_context() -> list[str]:
        """This is an override function that can be used to add additional context to the prompt"""
        return []

    def gpt_select_last() -> None:
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

    def gpt_apply_prompt(
        prompt: str,
        model: str,
        source: str = "",
        destination: str = "",
    ):
        """Apply an arbitrary prompt to arbitrary text"""

        text_to_process: GPTMessageItem = actions.user.gpt_get_source_text(source)
        if (
            text_to_process.get("text", "") == ""
            and text_to_process.get("image_url", "") == ""
        ):
            text_to_process = None  # type: ignore

        # Handle special cases in the prompt
        ### Ask is a special case, where the text to process is the prompted question, not selected text
        if prompt.startswith("ask"):
            text_to_process = format_message(prompt.removeprefix("ask"))
            prompt = "Generate text that satisfies the question or request given in the input."

        # Convert model name from the model list to actual model name or use default
        if model == "model":
            # Check for deprecated setting first for backward compatibility
            openai_model: str = settings.get("user.openai_model")  # type: ignore
            if openai_model != "do_not_use":
                logging.warning(
                    "The setting 'user.openai_model' is deprecated. Please use 'user.model_default_model' instead."
                )
                model = openai_model
            else:
                model = settings.get("user.model_default_model")  # type: ignore

        response = gpt_query(
            format_message(prompt), text_to_process, model, destination
        )

        actions.user.gpt_insert_response(response, destination)
        return response

    def gpt_pass(source: str = "", destination: str = "") -> None:
        """Passes a response from source to destination"""
        actions.user.gpt_insert_response(
            actions.user.gpt_get_source_text(source), destination
        )

    def gpt_help() -> None:
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

    def gpt_reformat_last(how_to_reformat: str, model: str) -> str:
        """Reformat the last model output"""
        PROMPT = f"""The last phrase was written using voice dictation. It has an error with spelling, grammar, or just general misrecognition due to a lack of context. Please reformat the following text to correct the error with the context that it was {how_to_reformat}."""
        last_output = actions.user.get_last_phrase()
        if last_output:
            actions.user.clear_last_phrase()
            return extract_message(
                gpt_query(format_message(PROMPT), format_message(last_output), model)
            )
        else:
            notify("No text to reformat")
            raise Exception("No text to reformat")

    def gpt_insert_response(
        gpt_message: GPTMessageItem,
        method: str = "",
        cursorless_destination: Any = None,
    ) -> None:
        """Insert a GPT result in a specified way"""
        # Use a custom default if nothing is provided and the user has set
        # a different default destination
        if method == "":
            method = settings.get("user.model_default_destination")

        # If threading is enabled, and the window is open, refresh the confirmation GUI
        # unless the user explicitly wanted to pass the result to the window without viewing the rest of the thread
        if (
            GPTState.thread_enabled
            and confirmation_gui.showing
            and not method == "window"
            # If they ask for thread or newThread specifically,
            # it should be pushed to the thread and not just refreshed
            and not method == "thread"
            and not method == "newThread"
        ):
            # Skip inserting the response if the user is just viewing the thread in the window
            actions.user.confirmation_gui_refresh_thread()
            return

        match method:
            case "thread" | "newThread" as t:
                if t == "newThread":
                    GPTState.new_thread()
                GPTState.push_thread(format_messages("user", [gpt_message]))
                actions.user.confirmation_gui_refresh_thread()
                return

        if gpt_message.get("type") != "text":
            actions.app.notify(
                f"Tried to insert an image to {method}, but that is not currently supported. To insert an image to this destination use a prompt to convert it to text."
            )
            return

        message_text_no_images = extract_message(gpt_message)
        match method:
            case "above":
                actions.key("left")
                actions.edit.line_insert_up()
                GPTState.last_was_pasted = True
                actions.user.paste(message_text_no_images)
            case "below":
                actions.key("right")
                actions.edit.line_insert_down()
                GPTState.last_was_pasted = True
                actions.user.paste(message_text_no_images)
            case "clipboard":
                clip.set_text(message_text_no_images)
            case "snip":
                actions.user.insert_snippet(message_text_no_images)
            case "context":
                GPTState.push_context(gpt_message)
            case "newContext":
                GPTState.clear_context()
                GPTState.push_context(gpt_message)
            case "appendClipboard":
                if clip.text() is not None:
                    clip.set_text(clip.text() + "\n" + message_text_no_images)  # type: ignore Unclear why this is throwing a type error in pylance
                else:
                    clip.set_text(message_text_no_images)
            case "browser":
                builder = Builder()
                builder.h1("Talon GPT Result")
                for line in message_text_no_images.split("\n"):
                    builder.p(line)
                builder.render()
            case "textToSpeech":
                try:
                    actions.user.tts(message_text_no_images)
                except KeyError:
                    notify("GPT Failure: text to speech is not installed")

            # Although we can insert to a cursorless destination, the cursorless_target capture
            # Greatly increases DFA compliation times and should be avoided if possible
            case "cursorless":
                actions.user.cursorless_insert(
                    cursorless_destination, message_text_no_images
                )
            # Don't add to the window twice if the thread is enabled
            case "window":
                # If there was prior text in the confirmation GUI and the user
                # explicitly passed new text to the gui, clear the old result
                GPTState.text_to_confirm = message_text_no_images
                actions.user.confirmation_gui_append(message_text_no_images)
            case "chain":
                GPTState.last_was_pasted = True
                actions.user.paste(message_text_no_images)
                actions.user.gpt_select_last()

            case "paste":
                GPTState.last_was_pasted = True
                actions.user.paste(message_text_no_images)
            # If the user doesn't specify a method assume they want to paste.
            # However if they didn't specify a method when the confirmation gui
            # is showing, assume they don't want anything to be inserted
            case _ if not confirmation_gui.showing:
                GPTState.last_was_pasted = True
                actions.user.paste(message_text_no_images)
            # Don't do anything if none of the previous conditions were valid
            case _:
                pass

    def gpt_get_source_text(spoken_text: str) -> GPTMessageItem:
        """Get the source text that is will have the prompt applied to it"""
        match spoken_text:
            case "clipboard":
                return format_clipboard()
            case "context":
                if GPTState.context == []:
                    notify("GPT Failure: Context is empty")
                    raise Exception(
                        "GPT Failure: User applied a prompt to the phrase context, but there was no context stored"
                    )
                return format_message(messages_to_string(GPTState.context))
            case "thread":
                # TODO: Do we want to throw an exception here if the thread is empty?
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
                    notify("GPT Failure: No last dictation to reformat")
                    raise Exception(
                        "GPT Failure: User applied a prompt to the phrase last Talon Dictation, but there was no text to reformat"
                    )
            case "this" | _:
                return format_message(actions.edit.selected_text())
