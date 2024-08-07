mode: command
tag: user.cursorless
-

# Apply a prompt to any text, and output it any target
# Paste it to the cursor if no target is specified
model <user.modelSimplePrompt> <user.cursorless_target> [<user.cursorless_destination>]$:
    text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(user.modelSimplePrompt, text)
    default_destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(cursorless_destination or default_destination, result)

# Add the text from a cursorless target to your context
model pass <user.cursorless_target> to context$:
    text = user.cursorless_get_text(cursorless_target)
    user.gpt_push_context(text)

# Add the text from a cursorless target to a new context
model pass <user.cursorless_target> to new context'$:
    text = user.cursorless_get_text(cursorless_target)
    user.gpt_clear_context()
    user.gpt_push_context(text)

# Add the text from a cursorless target to the current thread
model pass <user.cursorless_target> to thread$:
    text = user.cursorless_get_text(cursorless_target)
    user.gpt_push_thread(text)

# Add the text from a cursorless target to a new thread
model pass <user.cursorless_target> to new thread$:
    text = user.cursorless_get_text(cursorless_target)
    user.gpt_clear_thread()
    user.gpt_push_thread(text)

# Applies an arbitrary prompt from the clipboard to a cursorless target.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
model apply [from] clip <user.cursorless_target>$:
    prompt = clip.text()
    text = user.cursorless_get_text_list(cursorless_target)
    result = user.gpt_apply_prompt(prompt, text)
    default_destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(default_destination, result)
