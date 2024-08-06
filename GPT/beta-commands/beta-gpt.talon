mode: command
tag: user.gpt_beta
-

# Find all Talon commands that match the user's text
{user.modelAlias} find <user.text>: user.gpt_find_talon_commands(user.text)

# Using the context of the text on the clipboard, update the selected text
{user.modelAlias} blend paste:
    destination_text = edit.selected_text()
    result = user.gpt_blend(clip.text(), destination_text)

# Pass the raw text of a prompt to a destination without actually calling GPT with it
{user.modelAlias} pass <user.modelPrompt> [{user.modelDestination}]:
    user.gpt_insert_response(modelPrompt, modelDestination or "")
