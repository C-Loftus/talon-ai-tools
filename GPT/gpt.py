import os
from typing import Any

from talon import Module, actions, clip

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import (
    GPTState,
    generate_payload,
    gpt_send_request,
    notify,
    paste_and_modify,
)

mod = Module()


def gpt_query(prompt: str, content: str, modifier: str = "") -> str:
    """Send a prompt to the GPT API and return the response"""

    # Reset state before pasting
    GPTState.last_was_pasted = False

    headers, data = generate_payload(prompt, content, None, modifier)

    response = gpt_send_request(headers, data)
    GPTState.last_response = response
    if modifier == "thread":
        GPTState.push_thread(prompt)
        GPTState.push_thread(content)
        GPTState.push_thread(response)
    return response


@mod.action_class
class UserActions:
    def gpt_blend(source_text: str, destination_text: str):
        """Blend all the source text and send it to the destination"""
        prompt = f"""
        Act as a text transformer. I will provide source text and destination text. Your task is to modify the destination text based on the content of the source text, ensuring a natural and coherent flow by reordering and renaming as necessary. Return only the final text with no decoration for insertion into a document in the specified language.

        Here is the destination text:
        {destination_text}


        Please return only the final text. The source texts are separated by '---'.
        """
        return gpt_query(prompt, source_text)

    def gpt_blend_list(source_text: list[str], destination_text: str):
        """Blend all the source text as a list and send it to the destination"""

        return actions.user.gpt_blend("\n---\n".join(source_text), destination_text)

    def gpt_clear_context():
        """Reset the stored context"""
        GPTState.clear_context()

    def gpt_new_thread():
        """Create a new thread"""
        GPTState.new_thread()

    def gpt_push_context(context: str):
        """Add the selected text to the stored context"""
        GPTState.push_context(context)

    def gpt_custom_user_context() -> list[str]:
        """This is an override function that can be used to add additional context to the prompt"""
        return []

    def gpt_select_last():
        """select all the text in the last GPT output"""
        if not GPTState.last_was_pasted:
            notify("GPT Error: No text to select")
            raise RuntimeError

        lines = GPTState.last_response.split("\n")
        for _ in lines[:-1]:
            actions.edit.extend_up()
        actions.edit.extend_line_end()
        for _ in lines[0]:
            actions.edit.extend_left()

    def gpt_apply_prompt(
        prompt: str, text_to_process: str | list[str], modifier: str = ""
    ) -> str:
        """Apply an arbitrary prompt to arbitrary text"""
        text_to_process = (
            " ".join(text_to_process)
            if isinstance(text_to_process, list)
            else text_to_process
        )

        # Apply modifiers to prompt before handling special cases
        match modifier:
            case "snip":
                prompt += "\n\nPlease return the response as a snippet with placeholders. A snippet can control cursors and text insertion using constructs like tabstops ($1, $2, etc., with $0 as the final position). Linked tabstops update together. Placeholders, such as ${1:foo}, allow easy changes and can be nested (${1:another ${2:placeholder}}). Choices, using ${1|one,two,three|}, prompt user selection."

        # Ask is a special case, where the text to process is the prompted question, not the selected text
        if prompt.startswith("ask"):
            text_to_process = prompt.removeprefix("ask")
            prompt = (
                """Generate text that satisfies the question or request given here:"""
            )
        # If the user is just moving the source to the destination, we don't need to apply a query
        elif prompt == "pass":
            return text_to_process

        return gpt_query(prompt, text_to_process, modifier)

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
            return gpt_query(PROMPT, last_output)
        else:
            notify("GPT Error: No text to reformat")
            raise RuntimeError

    def gpt_insert_response(
        result: str,
        method: str = "",
        modifier: str = "",
        cursorless_destination: Any = None,
    ):
        """Insert a GPT result in a specified way"""
        match method:
            case "above":
                actions.key("left")
                actions.edit.line_insert_up()
                GPTState.last_was_pasted = True
                paste_and_modify(result, modifier)
            case "below":
                actions.key("right")
                actions.edit.line_insert_down()
                GPTState.last_was_pasted = True
                paste_and_modify(result, modifier)
            case "clipboard":
                clip.set_text(result)
            case "context":
                GPTState.push_context(result)
            case "newContext":
                GPTState.clear_context()
                GPTState.push_context(result)
            case "thread":
                GPTState.push_thread(result)
            case "newThread":
                GPTState.new_thread()
                GPTState.push_thread(result)
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
                    notify("GPT Error: Text to speech is not installed")
                    raise RuntimeError

            # Although we can insert to a cursorless dpestination, the cursorless_target capture
            # Greatly increases DFA compliation times and should be avoided if possible
            case "cursorless":
                actions.user.cursorless_insert(cursorless_destination, result)
            case "paste" | _:
                GPTState.last_was_pasted = True
                paste_and_modify(result, modifier)

    def gpt_get_source_text(spoken_text: str) -> str:
        """Get the source text that is will have the prompt applied to it"""
        match spoken_text:
            case "clipboard":
                clipboard_text = clip.text()
                if clipboard_text is None:
                    if clip.image():
                        return "__IMAGE__"
                    else:
                        notify(
                            "GPT Error: User applied a prompt to the clipboard, but there was no clipboard text or image stored"
                        )
                        raise RuntimeError
                return clipboard_text
            case "context":
                # We have to return this here since we don't want to return all the metadata associated with it
                # We resolve the data inside at calltime
                return GPTState.context
            case "thread":
                # We have to return this here since we don't want to return all the metadata associated with it
                # We resolve the data inside at calltime
                return GPTState.thread
            case "gptResponse":
                if GPTState.last_response == "":
                    notify(
                        "GPT Error: User applied a prompt to the phrase GPT response, but there was no GPT response stored"
                    )
                    raise RuntimeError
                return GPTState.last_response

            case "lastTalonDictation":
                last_output = actions.user.get_last_phrase()
                if last_output:
                    actions.user.clear_last_phrase()
                    return last_output
                else:
                    notify(
                        "GPT Failure: User applied a prompt to the phrase last Talon Dictation, but there was no text to reformat"
                    )
                    raise RuntimeError
            case "this" | _:
                return actions.edit.selected_text()
