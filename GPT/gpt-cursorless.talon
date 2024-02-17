mode: command
tag: user.cursorless
-

# Apply a prompt to any text, and output it any target
^model {user.staticPrompt} <user.cursorless_target> <user.cursorless_destination>$:
    text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(user.staticPrompt, text)
    user.cursorless_insert(cursorless_destination, result)

tag(): user.gpt_beta
