from talon import Context, Module

mod = Module()
ctx = Context()
# Stores all our prompts that don't require arguments
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")
mod.list("customPrompt", desc="Custom user-defined GPT prompts")
mod.list("modelPrompt", desc="GPT Prompts")
mod.list("model", desc="The name of the model")
mod.list("modelDestination", desc="What to do after returning the model response")
mod.list("modelSource", desc="Where to get the text from for the GPT")
mod.list("thread", desc="Which conversation thread to continue")


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(
    rule="{user.staticPrompt} | {user.customPrompt} | (please <user.text>) | (ask <user.text>)"
)
def modelPrompt(matched_prompt) -> str:
    return str(matched_prompt)


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(rule="{user.staticPrompt} | {user.customPrompt}")
def modelSimplePrompt(matched_prompt) -> str:
    return str(matched_prompt)


mod.setting(
    "model_default",
    type=str,
    default="gpt-4o-mini",
    desc="The default model to use when no specific model is specified in the command",
)

mod.setting(
    "openai_model",
    type=str,
    default="do_not_use",
    desc="DEPRECATED: Use model_default instead. This setting is maintained for backward compatibility only.",
)

mod.setting(
    "model_temperature",
    type=float,
    default=-1.0,
    desc="DEPRECATED: Use llm_options or api_options in models.json instead.",
)

mod.setting(
    "model_default_destination",
    type=str,
    default="paste",
    desc="The default insertion destination. This can be overridden contextually to provide application level defaults.",
)

mod.setting(
    "model_endpoint",
    type=str,
    default="https://api.openai.com/v1/chat/completions",
    desc='The endpoint to send the model requests to. If "llm" is specified instead of a url, the llm CLI tool is used when routing all language model requests (see https://github.com/simonw/llm).',
)

mod.setting(
    "model_llm_path",
    type=str,
    default="llm",
    desc='The path to the executable for the "llm" CLI tool. Only used if model_endpoint is set to "llm", signifying that you want to use "llm" as the manager for all your language model requests',
)

mod.setting(
    "model_verbose_notifications",
    type=bool,
    default=True,
    desc="If true, show notifications when model starts and completes successfully.",
)

mod.setting(
    "model_system_prompt",
    type=str,
    default="You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested. If the user requests code generation, output just code and not additional natural language explanation.",
    desc="The default system prompt that informs the way the model should behave at a high level",
)


mod.setting(
    "model_shell_default",
    type=str,
    default="bash",
    desc="The default shell for outputting model shell commands",
)

mod.setting(
    "model_window_char_width",
    type=int,
    default=80,
    desc="The default window width (in characters) for showing model output",
)
