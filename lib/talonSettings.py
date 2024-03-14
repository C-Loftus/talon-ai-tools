from typing import Literal

from talon import Module

mod = Module()
mod.tag("gpt_beta", desc="Tag for enabling beta GPT commands")
# Stores all our prompts that don't require arguments
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")

mod.setting(
    "openai_model", type=Literal["gpt-3.5-turbo", "gpt-4"], default="gpt-3.5-turbo"
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
    default="You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting unless it is requested.",
    desc="The default system prompt that informs the way the model should behave at a high level",
)


mod.setting("openDescriptionInBrowser", type=bool, default=True)
mod.setting("maxDescriptionTokens", type=int, default=300)

mod.list("descriptionPrompt", desc="Prompts for describing images")
