mode: command
tag: user.cursorless
-

# Apply a prompt to any text, and output it any target
# Paste it to the cursor if no target is specified
model <user.modelPrompt> <user.cursorless_target> [<user.cursorless_destination>]$:
    text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(user.modelPrompt, text)
    default_destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(cursorless_destination or default_destination, result)

# Applies an arbitrary prompt from the clipboard to selected text and pastes the result.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
model apply [from] clip <user.cursorless_target>$:
    prompt = clip.text()
    text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(prompt, text)
    default_destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(default_destination, result)
