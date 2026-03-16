tag: user.gpt_semantic_preview_open
-

# Example: `model semantic run plan`.
# Execute the currently previewed semantic plan.
{user.model} semantic run plan$: user.gpt_semantic_run_pending()

# Example: `model semantic cancel plan`.
# Discard the currently previewed semantic plan.
{user.model} semantic cancel plan$: user.gpt_semantic_cancel_pending()

# Example: `model semantic copy plan`.
# Copy the currently previewed semantic JSON plan.
{user.model} semantic copy plan$: user.gpt_semantic_copy_pending()
