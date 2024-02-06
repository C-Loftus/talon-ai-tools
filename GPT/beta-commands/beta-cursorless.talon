mode: command
tag: user.gpt_beta
app: vscode
# can't match on user.cursorless without ORing the gpt.beta tag, so just match on vscode
-

^model please <user.text> <user.cursorless_target>$:
    prompt = user.text
    txt = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(prompt, txt)
    user.cursorless_insert(cursorless_destination, result)
