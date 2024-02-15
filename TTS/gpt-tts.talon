# TTS comes from the sight-free-talon repo
# This repo is a dependency for use of TTS
tag: user.sightFreeTalonInstalled

-

echo {user.staticPrompt}$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(user.staticPrompt, text)
    user.tts(result)

echo ask <user.text>$:
    result = user.gpt_answer_question(text)
    user.tts(result)
