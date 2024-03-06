echo (describe | image) (image | describe):
    result = user.image_describe_clipboard("")
    user.tts(result)

echo describe [{user.descriptionPrompt}]$:
    result = user.image_describe_clipboard(descriptionPrompt or "")
    user.tts(result)

echo describe window [{user.descriptionPrompt}]$:
    user.screenshot_window_clipboard()
    result = user.image_describe_clipboard(descriptionPrompt or "")
    user.tts(result)

echo describe screen [{user.descriptionPrompt}]$:
    user.screenshot_clipboard()
    result = user.image_describe_clipboard(descriptionPrompt or "")
    user.tts(result)
