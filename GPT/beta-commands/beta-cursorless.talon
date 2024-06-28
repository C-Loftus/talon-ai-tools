mode: command
tag: user.gpt_beta
app: vscode
# can't match on user.cursorless without ORing the gpt.beta tag, so just match on vscode
-

# model blend takes a X and a Y and returns a Z, where Z is a blend of X and Y
#   Example `model blend block this to block next`
model blend <user.cursorless_target> to <user.cursorless_target>:
    target_text = user.cursorless_get_text_list(cursorless_target_1)
    destination_text = user.cursorless_get_text(cursorless_target_2)
    default_destination = user.cursorless_create_destination(cursorless_target_2)
    result = user.gpt_blend_list(target_text, destination_text)
    user.cursorless_insert(default_destination, result)

model blend to <user.cursorless_target>:
    target_text = edit.selected_text()
    destination_text = user.cursorless_get_text(cursorless_target)
    default_destination = user.cursorless_create_destination(cursorless_target)
    result = user.gpt_blend(target_text, destination_text)
    user.cursorless_insert(default_destination, result)

model blend <user.cursorless_target>:
    target_text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_blend_list(target_text, edit.selected_text())
    user.paste(result)
