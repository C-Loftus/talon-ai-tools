mode: command

-

# Ask a question in the voice command and the AI will answer it.
model ask <user.text>$:
    user.gpt_answer_question(text)

# Runs a model prompt on the selected text and pastes the result.
model {user.staticPrompt} [this]$:
    text = edit.selected_text()
    user.gpt_apply_prompt(user.staticPrompt, text)

# Runs a model prompt on the selected text and sets the result to the clipboard
model clip {user.staticPrompt} [this]$:
    text = edit.selected_text()
    user.gpt_apply_prompt_clip(user.staticPrompt, text)

# Say your prompt directly and the AI will apply it to the selected text
model please <user.text>$:
    prompt = user.text
    txt = edit.selected_text()
    user.gpt_apply_prompt(prompt, txt)

# Applies an arbitrary prompt from the clipboard to selected text and pastes the result.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
model apply [from] clip$:
    prompt = clip.text()
    text = edit.selected_text()
    user.gpt_apply_prompt(prompt, text)

# Shows the list of available prompts
model help$:
    user.gpt_help()
