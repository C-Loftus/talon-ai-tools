# Shows the list of available prompts
model help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clip to browser` -> Fixes the grammar of the text on the clipboard and opens in browser`
model [{user.modelModifier}] <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]:
    user.gpt_apply_prompt(modelPrompt, modelSource or "", modelDestination or "", modelModifier or "")

# Select the last GPT response so you can edit it further
model take response: user.gpt_select_last()

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

# Clear the context stored in the model
model clear context: user.gpt_clear_context()

# Create a new thread which is similar to a conversation with the model
# A thread allows the model to access data from the previous queries in the same thread
model clear thread: user.gpt_clear_thread()
model enable thread: user.gpt_enable_threading()
model disable thread: user.gpt_disable_threading()
