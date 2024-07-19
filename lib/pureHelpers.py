import platform
import re

"""
Everything in this file are functions which do not interact with the
system via talon or the model via API calls
"""


def remove_wrapper(text: str):
    """Remove the string wrapper from the str representation of a command"""
    # different command wrapper for Linux.
    if platform.system() == "Linux":
        regex = r"^.*?'(.*?)'.*?$"
    else:
        # TODO condense these regexes. Hard to test between platforms
        # since the wrapper is slightly different
        regex = r'[^"]+"([^"]+)"'
    match = re.search(regex, text)
    return match.group(1) if match else text


def strip_markdown(text: str) -> str:
    """Remove markdown from the text"""
    # Define the regex pattern to match the markdown code block syntax

    # Don't allow spaces after language identifier?
    # strict_pattern = r"```[a-zA-Z]*\n([\s\S]*?)```"

    pattern = r"```[a-zA-Z]*\s*\n([\s\S]*?)```"

    # Use re.sub to replace the matched pattern with the code inside the block
    stripped_code = re.sub(pattern, r"\1", text)

    return stripped_code.strip()
