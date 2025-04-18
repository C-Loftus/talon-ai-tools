# Shows the list of available prompts
{user.model} help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clip to browser` -> Fixes the grammar of the text on the clipboard and opens in browser`
#   Example: `four o mini explain this` -> Uses gpt-4o-mini model to explain the selected text
#   Example: `model and explain this` -> Explains the selected text and pastes in place, continuing the most recent conversation thread
{user.model} [{user.modelThread}] <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]$:
    user.gpt_apply_prompt(modelPrompt, model, modelThread or "", modelSource or "", modelDestination or "")

# Select the last GPT response so you can edit it further
{user.model} take response: user.gpt_select_last()

# Applies an arbitrary prompt from the clipboard to selected text and pastes the result.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
{user.model} [{user.modelThread}] apply [from] clip$:
    prompt = clip.text()
    text = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, model, modelThread or "", text)
    user.paste(result)

# Reformat the last dictation with additional context or formatting instructions
{user.model} [{user.modelThread}] [nope] that was <user.text>$:
    result = user.gpt_reformat_last(text, model, modelThread or "")
    user.paste(result)

# Enable debug logging so you can more details about messages being sent
{user.model} start debug: user.gpt_start_debug()

# Disable debug logging
{user.model} stop debug: user.gpt_stop_debug()
