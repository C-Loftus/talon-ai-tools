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

# Clear the context stored in the model
model context clear: user.gpt_clear_context()

# Reduce the length of context stored in the model by using a GPT summarization
model context optimize: user.gpt_optimize_context()

# Create a new thread which is similar to a conversation with the model
# A thread allows the model to access data from the previous queries in the same thread
model thread new: user.gpt_new_thread()

# Run a GPT command in a thread; This allows it to access context from previous requests in the thread
model thread <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]:
    text = user.gpt_get_source_text(modelSource or "")
    result = user.gpt_apply_prompt(modelPrompt, text, "thread")
    user.gpt_insert_response(result, modelDestination or "", "thread")

# Reduce the length of the current thread by using a GPT summarization
model thread optimize: user.gpt_optimize_thread()

# Pass the data in the current thread to a destination
model pass thread {user.modelDestination}:
    text = user.gpt_get_thread()
    user.gpt_insert_response(text, modelDestination or "")
