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

model blend clip to <user.cursorless_target>:
    clipboard_text = clip.text()
    destination_text = user.cursorless_get_text(cursorless_target)
    default_destination = user.cursorless_create_destination(cursorless_target)
    result = user.gpt_blend(clipboard_text, destination_text)
    user.cursorless_insert(default_destination, result)
