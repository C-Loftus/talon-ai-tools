mode: command

-
# Ask a question in the voice command and the AI will answer it.
model ask <user.text>:
    result = user.gpt_answer_question(text)
    user.paste(result)

# Runs a model prompt on the selected text and pastes the result.
^model {user.staticPrompt} [this]$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(user.staticPrompt, text)
    user.paste(result)

# Runs a model prompt on the selected text and sets the result to the clipboard
^model clip {user.staticPrompt}$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(user.staticPrompt, text)
    clip.set_text(result)

# Say your prompt directly and the AI will apply it to the selected text
^model please <user.text>$:
    prompt = user.text
    txt = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, txt)
    user.paste(result)

# TODO: make this less verbose in output
# Shows the list of available prompts
^model help$:
    user.help_list("user.promptNoArgument")
