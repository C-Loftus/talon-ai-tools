mode: command
tag: user.cursorless

-

# Apply a prompt to any text, and output it any target
^model {user.staticPrompt} <user.cursorless_target> <user.cursorless_destination>$:
    text = user.cursorless_get_text_list(cursorless_target)
    user.gpt_apply_cursorless_prompt(user.staticPrompt, text, cursorless_destination)

# # Say an arbitrary prompt and apply it to any target
# ^model please <user.text> <user.cursorless_target>$:
#     prompt = user.text
#     txt = user.cursorless_get_text_list(cursorless_target)
#     result = user.gpt_apply_prompt(prompt, txt)
#     user.cursorless_insert(cursorless_destination, result)
