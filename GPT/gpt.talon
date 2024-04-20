# Ask a question in the voice command and the AI will answer it.
model ask <user.text>$:
    result = user.gpt_answer_question(text)
    user.paste(result)

# Runs a model prompt on the selected text and pastes the result.
model <user.modelPrompt> [this]$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.paste(result)

# Runs a model prompt on the selected text and sets the result to the clipboard
model <user.modelPrompt> [this] (then | and) (clip | copy) [it]$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(modelPrompt, text)
    clip.set_text(result)

# Runs a model prompt on the selected text and sets the selection to the pasted response
model <user.modelPrompt> [this] (then | and) select [it]$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.paste_and_select(result)

# Say your prompt directly and the AI will apply it to the selected text
model please <user.text>$:
    prompt = user.text
    txt = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, txt)
    user.paste(result)

# Applies an arbitrary prompt from the clipboard to selected text and pastes the result.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
model apply [from] clip$:
    prompt = clip.text()
    text = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, text)
    user.paste(result)

# Shows the list of available prompts
model help$: user.gpt_help()

# Reformat the last dictation with additional context or formatting instructions
model [nope] that was <user.text>$:
    result = user.gpt_reformat_last(text)
    user.paste(result)
