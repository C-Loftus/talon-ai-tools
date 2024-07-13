# Shows the list of available prompts
model help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clip to browser` -> Fixes the grammar of the text on the clipboard and opens in browser`
model <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]:
    text = user.gpt_get_source_text(modelSource or "")
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.gpt_insert_response(result, modelDestination or "")

# Select the last GPT response so you can edit it further
model take response: user.gpt_select_last()

# Modifies a model command to be inserted as a snippet for VSCode instead of a standard paste
# Otherwise same grammar as standard `model` command
model snip <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]:
    text = user.gpt_get_source_text(modelSource or "")
    result = user.gpt_apply_prompt(modelPrompt, text, "snip")
    user.gpt_insert_response(result, modelDestination or "", "snip")

# Modifies a model comand to always insert with the text selected
# Useful for chaining together prompts immediately after they return
# Otherwise same grammar as standard `model` command
model chain <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]:
    text = user.gpt_get_source_text(modelSource or "")
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.gpt_insert_response(result, modelDestination or "", "chain")

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
