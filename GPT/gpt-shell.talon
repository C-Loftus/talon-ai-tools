mode: command
-

# Generate a shell command by specifying what you want it to do
# You have to explicitly confirm the output of the model before
# it is pasted so nothing is accidentally executed
{user.model} [{user.thread}] shell <user.text>$:
    result = user.gpt_generate_shell(user.text, model, thread or "")
    user.confirmation_gui_append(result)

# Generate a SQL command by specifying what you want it to return
{user.model} [{user.thread}] (sequel | sql) <user.text>$:
    result = user.gpt_generate_sql(user.text, model, thread or "")
    user.confirmation_gui_append(result)
