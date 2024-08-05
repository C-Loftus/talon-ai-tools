tag: user.model_window_open
-

# Confirm and paste the output of the model
^paste response$: user.paste_model_confirmation_gui()

# Confirm and paste the output of the model selected
^chain response$:
    user.paste_model_confirmation_gui()
    user.gpt_select_last()

^copy response$: user.copy_model_confirmation_gui()

# Deny the output of the model and discard it
^discard response$: user.close_model_confirmation_gui()
