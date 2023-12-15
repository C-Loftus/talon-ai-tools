mode: command

-

# Ask your question in the voice command and the AI will answer it.
model ask <user.text>:
    result = user.gpt_answer_question(text)
    user.paste(result)

# Runs a model prompt on the selected text and pastes the result.
^model {user.promptNoArgument}$:
    result = user.gpt_prompt_no_argument(user.promptNoArgument)
    user.paste(result)

# Runs a model prompt on the selected text and sets the result to the clipboard
^model clip {user.promptNoArgument}$:
    result = user.gpt_answer_question(user.promptNoArgument)
    clip.set_text(result)

# TODO: make this less verbose in output
# Shows the list of available prompts
^model help$:
    user.help_list("user.promptNoArgument")
