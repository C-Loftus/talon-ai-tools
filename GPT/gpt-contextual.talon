# Clear the context stored in the model
model context clear: user.gpt_clear_context()

# Create a new thread which is similar to a conversation with the model
# A thread allows the model to access data from the previous queries in the same thread
model thread new: user.gpt_new_thread()
