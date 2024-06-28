mode: command
tag: user.gpt_beta
-

# Find all Talon commands that match the user's text
model find <user.text>: user.gpt_find_talon_commands(user.text)

# Using the context of the text on the clipboard, update the selected text
model blend [from] clip:
    clipboard_text = clip.text()
    destination_text = edit.selected_text()
    result = user.gpt_blend(clipboard_text, destination_text)
    user.gpt_insert_response(result, "")

# Say your prompt directly and the AI will apply it to the selected text
model please <user.text>$:
    utterance = user.text
    txt = edit.selected_text()
    user.gpt_dynamic_request(utterance, txt)

# Runs a model prompt on the selected text and pastes the result.
model please <user.modelPrompt> [this]$:
    text = edit.selected_text()
    user.gpt_dynamic_request(user.modelPrompt, text)
