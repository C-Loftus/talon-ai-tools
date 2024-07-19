mode: command
tag: user.gpt_beta
-

# Find all Talon commands that match the user's text
model find <user.text>: user.gpt_find_talon_commands(user.text)

# Using the context of the text on the clipboard, update the selected text
model blend clip:
    destination_text = edit.selected_text()
    result = user.gpt_blend(user.gpt_get_source_text("clipboard"), destination_text)
    user.gpt_insert_response(result, "")

# Pass the raw text of a prompt to a destination without actually calling GPT with it
model pass <user.modelPrompt> [{user.modelDestination}]:
    user.gpt_insert_response(modelPrompt, modelDestination or "")
