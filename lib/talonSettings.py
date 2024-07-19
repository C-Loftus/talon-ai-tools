from typing import Literal

from talon import Context, Module

mod = Module()
ctx = Context()
mod.tag("gpt_beta", desc="Tag for enabling beta GPT commands")
# Stores all our prompts that don't require arguments
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")
mod.list("customPrompt", desc="Custom user-defined GPT prompts")
mod.list("modelPrompt", desc="GPT Prompts")
mod.list("modelDestination", desc="What to do after returning the model response")
mod.list("modelSource", desc="Where to get the text from for the GPT")


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(
    rule="{user.staticPrompt} | {user.customPrompt} | (please <user.text>) | (ask <user.text>) | pass"
)
def modelPrompt(matched_prompt) -> str:
    return str(matched_prompt)


mod.setting(
    "openai_model",
    type=Literal["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"],
    default="gpt-4o-mini",
)

mod.setting(
    "model_temperature",
    type=float,
    default=0.6,
    desc="The temperature of the model. Higher values make the model more creative.",
)

mod.setting(
    "model_endpoint",
    type=str,
    default="https://api.openai.com/v1/chat/completions",
    desc="The endpoint to send the model requests to",
)

mod.setting(
    "model_system_prompt",
    type=str,
    default="You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested.",
    desc="The default system prompt that informs the way the model should behave at a high level",
)

mod.setting(
    "model_shell_default",
    type=str,
    default="bash",
    desc="The default shell for outputting model shell commands",
)

# Image description settings
mod.setting("openDescriptionInBrowser", type=bool, default=True)
mod.setting("maxDescriptionTokens", type=int, default=300)
mod.list("descriptionPrompt", desc="Prompts for describing images")
