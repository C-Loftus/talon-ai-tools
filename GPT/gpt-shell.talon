mode: command
-

# You have to explicitly confirm the output of the model before
# it is pasted so nothing is accidentally executed
model shell <user.text>$:
    result = user.gpt_generate_shell(user.text)
    user.add_to_confirmation_gui(result)

model (sequel | sql) <user.text>$:
    result = user.gpt_generate_sql(user.text)
    user.add_to_confirmation_gui(result)

# Confirm and paste the output of the model
^paste model output$: user.paste_model_confirmation_gui()

^copy model output$: user.copy_model_confirmation_gui()

# Deny the output of the model and discard it
^deny model output$: user.close_model_confirmation_gui()
