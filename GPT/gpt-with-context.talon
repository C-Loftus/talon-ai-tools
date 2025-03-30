# All of the following commands allow the user to store or manipulate context
# `context` represents additional info that can persist across conversations

# Passes a model source to a model destination unchanged; useful for debugging,
# passing around context, or chaining the responses of previous prompts
# If the source is omitted, default to selected text; If the destination is omitted default to paste
# Example: `model pass this to context`
# Example: `model pass context to clip`
# Example: `model pass clip to this`
{user.model} pass ({user.modelSource} | {user.modelDestination} | {user.modelSource} {user.modelDestination})$:
    user.gpt_pass(modelSource or "", modelDestination or "")

# Clear the context stored in the model
{user.model} clear context: user.gpt_clear_context()
