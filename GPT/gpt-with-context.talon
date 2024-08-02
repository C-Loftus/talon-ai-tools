# Clear the context stored in the model
model context clear: user.gpt_clear_context()

# Create a new thread which is similar to a conversation with the model
# A thread allows the model to access data from the previous queries in the same thread
model thread new: user.gpt_new_thread()

# Run a GPT command in a thread; This allows it to access context from previous requests in the thread
model thread <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]:
    text = user.gpt_get_source_text(modelSource or "")
    result = user.gpt_apply_prompt(modelPrompt, text, "thread")
    user.gpt_insert_response(result, modelDestination or "")
