mode: command
tag: user.gpt_beta

-

# Say your prompt directly and the AI will apply it to the selected text
model go <user.text>$:
    utterance = user.text
    txt = edit.selected_text()
    user.gpt_go(utterance, txt)

# Runs a model prompt on the selected text and pastes the result.
model go {user.staticPrompt} [this]$:
    text = edit.selected_text()
    user.gpt_go(user.staticPrompt, text)
