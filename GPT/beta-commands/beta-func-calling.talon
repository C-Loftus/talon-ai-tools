mode: command
tag: user.gpt_beta
-

# Say your prompt directly and the AI will apply it to the selected text
model please <user.text>$:
    utterance = user.text
    txt = edit.selected_text()
    user.gpt_dynamic_request(utterance, txt)

# Runs a model prompt on the selected text and pastes the result.
model please <user.modelPrompt> [this]$:
    text = edit.selected_text()
    user.gpt_dynamic_request(user.modelPrompt, text)
