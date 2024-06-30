# Shows the list of available prompts
model help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clipboard windowed` -> Fixes the grammar of the text on the clipboard and opens in browser`
model <user.modelPrompt> [{user.modelTextSource}] [{user.modelResponseMethod}]$:
    text = user.gpt_get_source_text(modelTextSource or "")
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.gpt_insert_response(result, modelResponseMethod or "")

# Ask a question in the voice command and the model will answer it.
#   Example: `model ask what is the meaning of life`
#   Example: `model ask generate a plan to learn Javascript in browser`
model ask <user.text> [{user.modelResponseMethod}]$:
    result = user.gpt_answer_question(text)
    user.gpt_insert_response(result, modelResponseMethod or "")

# Runs an arbitrary prompt on the selected text; inserts with paste by default
#   Example: `model please translate this into English`
#   Example: `model please reformat this code in a more imperative style clipped`
model please <user.text> [{user.modelResponseMethod}]$:
    prompt = user.text
    txt = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, txt)
    user.gpt_insert_response(result, modelResponseMethod or "")

# Applies an arbitrary prompt from the clipboard to selected text and pastes the result.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
model apply [from] clip$:
    prompt = clip.text()
    text = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, text)
    user.paste(result)

# Reformat the last dictation with additional context or formatting instructions
model [nope] that was <user.text>$:
    result = user.gpt_reformat_last(text)
    user.paste(result)

tag(): user.gpt_beta