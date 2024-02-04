mode: command
tag: user.cursorless

-

# Say your prompt directly and the AI will apply it to the selected text
model go <user.text>$:
    utterance = user.text
    txt = edit.selected_text()
    user.gpt_go(utterance, txt)

# Apply a prompt to any text, and output it any target
^model go {user.staticPrompt} <user.cursorless_target> <user.cursorless_destination>$:
    text = user.cursorless_get_text_list(cursorless_target)
    user.gpt_go_cursorless(user.staticPrompt, text, cursorless_destination)