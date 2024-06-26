# Ask a question in the voice command and the model will answer it.
model ask <user.text>$:
    result = user.gpt_answer_question(text)
    user.paste(result)

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below`
#   Example: `model explain this`
model <user.modelPrompt> [this] [{user.modelInsertionMethod}]$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.gpt_insert_response(result, modelInsertionMethod or "")

model blend clip:
    clipboard_text = clip.text()
    destination_text = edit.selected_text()
    result = user.model_blend(clipboard_text, destination_text)
    user.gpt_insert_response(result, "")

# Runs an arbitrary prompt on the selected text; inserts with paste by default
#   Example: `model please translate this into English`
#   Example: `model please reformat this code in a more imperative style clipped`
model please <user.text> [{user.modelInsertionMethod}]$:
    prompt = user.text
    txt = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, txt)
    user.gpt_insert_response(result, modelInsertionMethod or "")

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
