from concurrent.futures import ThreadPoolExecutor

from talon import Module, registry

from ...lib.HTMLBuilder import Builder
from ...lib.pureHelpers import remove_wrapper
from ..gpt import gpt_query

mod = Module()


@mod.action_class
class UserActions:
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
