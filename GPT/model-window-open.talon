tag: user.model_window_open
-

# Confirm and paste the output of the model
^paste response$: user.paste_model_confirmation_gui()

# Confirm and paste the output of the model selected
^chain response$:
    user.paste_model_confirmation_gui()
    user.gpt_select_last()

^copy response$: user.copy_model_confirmation_gui()
^pass response to context$: user.pass_context_model_confirmation_gui()
^pass response to thread$: user.pass_thread_model_confirmation_gui()

# Deny the output of the model and discard it
^discard response$: user.close_model_confirmation_gui()
