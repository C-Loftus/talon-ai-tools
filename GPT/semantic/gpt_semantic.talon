not tag: user.gpt_semantic_preview_open
-

# Example: `model semantic open text editor`.
# Generate a semantic plan from natural language.
{user.model} semantic <user.text>$: user.gpt_semantic_generate(text, model)

# Example: `model semantic repeat last`.
# Re-open the last confirmed plan in preview mode.
{user.model} semantic repeat last$: user.gpt_semantic_repeat_last()
