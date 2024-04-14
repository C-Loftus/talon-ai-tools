mode: command
tag: user.gpt_beta
app: vscode
# can't match on user.cursorless without ORing the gpt.beta tag, so just match on vscode
-

# Apply a prompt to any text, and output it any target
^model please <user.modelPrompt> <user.cursorless_target> [<user.cursorless_destination>]$:
    text_list = user.cursorless_get_text_list(cursorless_target)
    user.gpt_dynamic_request_cursorless(user.modelPrompt, text_list, cursorless_destination or 0)

^model please <user.text> <user.cursorless_target> [<user.cursorless_destination>]$:
    text_list = user.cursorless_get_text_list(cursorless_target)
    user.gpt_dynamic_request_cursorless(user.text, text_list, cursorless_destination or 0)
