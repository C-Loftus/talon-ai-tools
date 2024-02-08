mode: command
tag: user.gpt_beta

-

# Say your prompt directly and the AI will apply it to the selected text
model can you <user.text>$:
    utterance = user.text
    txt = edit.selected_text()
    user.gpt_can_you(utterance, txt)

# Runs a model prompt on the selected text and pastes the result.
model can you {user.staticPrompt} [this]$:
    text = edit.selected_text()
    user.gpt_can_you(user.staticPrompt, text)
