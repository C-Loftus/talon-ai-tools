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

model bring <user.cursorless_target> to <user.cursorless_target>$:
    clipboard_text = user.cursorless_get_text_list(cursorless_target_1)
    destination_text = user.cursorless_get_text(cursorless_target_2)
    result = user.gpt_smart_clipboard(clipboard_text, destination_text)
    default_destination = user.cursorless_create_destination(cursorless_target_2)
    user.cursorless_insert(default_destination, result)
