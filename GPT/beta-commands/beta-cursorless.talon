mode: command
tag: user.gpt_beta
app: vscode
# can't match on user.cursorless without ORing the gpt.beta tag, so just match on vscode
-

# Model Blend
# Combines source texts with a destination, preserving some of the destination's structure.
# ## Use Cases
# - Merging sentences
# - Adding types to a definition
# - Combining a template test with another, including comments for modifications
# - Prototyping the combination of two functions to see what a refactor would look like
# ## Example
# `model blend block this to block next`
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

on <user.cursorless_target> [responding {user.modelResponseMethod}] model (<user.modelPrompt> | please <user.text>):
    source_text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(modelPrompt or text, source_text)
    default_destination = user.cursorless_create_destination(cursorless_target)
    user.gpt_insert_response(result, modelResponseMethod or "", default_destination)

on <user.cursorless_target> responding at <user.cursorless_target> model (<user.modelPrompt> | please <user.text>):
    source_text = user.cursorless_get_text_list(cursorless_target_1)
    result = user.gpt_apply_prompt(modelPrompt or text, source_text)
    destination_text = user.cursorless_get_text(cursorless_target_2)
    default_destination = user.cursorless_create_destination(cursorless_target_2)
    user.cursorless_insert(default_destination, result)
