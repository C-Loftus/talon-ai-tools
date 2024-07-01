mode: command
tag: user.gpt_beta
-

# Find all Talon commands that match the user's text
model find <user.text>: user.gpt_find_talon_commands(user.text)

# Using the context of the text on the clipboard, update the selected text
model blend clipboard:
    clipboard_text = clip.text()
    destination_text = edit.selected_text()
    result = user.gpt_blend(clipboard_text, destination_text)
    user.gpt_insert_response(result, "")
