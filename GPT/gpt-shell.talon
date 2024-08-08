mode: command
-

# You have to explicitly confirm the output of the model before
# it is pasted so nothing is accidentally executed
{user.model} shell <user.text>$:
    result = user.gpt_generate_shell(user.text)
    user.add_to_confirmation_gui(result)

{user.model} (sequel | sql) <user.text>$:
    result = user.gpt_generate_sql(user.text)
    user.add_to_confirmation_gui(result)
