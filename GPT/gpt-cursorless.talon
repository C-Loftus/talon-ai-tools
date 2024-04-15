mode: command
tag: user.cursorless
-

# Apply a prompt to any text, and output it any target
# Paste it to the cursor if no target is specified
model <user.modelPrompt> <user.cursorless_target> [<user.cursorless_destination>]$:
    text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(user.modelPrompt, text)
    user.cursorless_or_paste_helper(cursorless_destination or 0, result)
