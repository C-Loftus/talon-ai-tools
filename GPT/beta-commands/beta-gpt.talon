mode: command
tag: user.gpt_beta
-

# By reversing the order to be source, adverb, action,
# we can place user.text at the end and get better recognition and easier chaining
[on {user.modelTextSource}] [responding {user.modelResponseMethod}] model (<user.modelPrompt> | please <user.text>):
    source_text = user.gpt_get_source_text(modelTextSource or "")
    result = user.gpt_apply_prompt(modelPrompt or text, source_text)
    user.gpt_insert_response(result, modelResponseMethod or "")

# Find all Talon commands that match the user's text
model find <user.text>: user.gpt_find_talon_commands(user.text)

# Using the context of the text on the clipboard, update the selected text
model blend [from] clip:
    clipboard_text = clip.text()
    destination_text = edit.selected_text()
    result = user.gpt_blend(clipboard_text, destination_text)
    user.gpt_insert_response(result, "")
