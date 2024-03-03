image describe [{user.descriptionPrompt}]$:
    user.image_describe_clipboard(descriptionPrompt or "")

image generate <user.text>$: user.image_generate(text)

image apply {user.generationPrompt}$: user.image_apply(generationPrompt)
