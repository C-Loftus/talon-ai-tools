image describe [{user.descriptionPrompt}]$:
    result = user.image_describe_clipboard(descriptionPrompt or "")
    user.paste(result)

image describe window [{user.descriptionPrompt}]$:
    user.screenshot_window_clipboard()
    result = user.image_describe_clipboard(descriptionPrompt or "")
    user.paste(result)

image describe screen [{user.descriptionPrompt}]$:
    user.screenshot_clipboard()
    result = user.image_describe_clipboard(descriptionPrompt or "")
    user.paste(result)

image generate <user.text>$: user.image_generate(text)
