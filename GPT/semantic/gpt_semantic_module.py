"""Talon module declarations for semantic commands.

Purpose:
- Registers semantic tag and settings used by runtime, parser, and executor.

Called from:
- Loaded automatically by Talon at startup/import time.
"""

from talon import Module

from .gpt_semantic_prompt import DEFAULT_SYSTEM_PROMPT

mod = Module()
mod.tag(
    "gpt_semantic_preview_open",
    desc="Enable model semantic run/cancel/copy commands while preview is visible",
)

mod.setting(
    "gpt_semantic_max_steps",
    type=int,
    default=12,
    desc="Maximum semantic plan step count",
)
mod.setting(
    "gpt_semantic_max_total_sleep_ms",
    type=int,
    default=2000,
    desc="Maximum total sleep duration for semantic plans",
)
mod.setting(
    "gpt_semantic_max_insert_chars",
    type=int,
    default=500,
    desc="Maximum insert_text payload length in semantic plans",
)
mod.setting(
    "gpt_semantic_debug",
    type=bool,
    default=False,
    desc="Enable debug logging for model semantic internals",
)
mod.setting(
    "gpt_semantic_app_focus_timeout_ms",
    type=int,
    default=3500,
    desc="Maximum wait for app focus after launch_app/switch_app steps",
)
mod.setting(
    "gpt_semantic_step_settle_ms",
    type=int,
    default=180,
    desc="Small delay after UI-sensitive steps to reduce race conditions",
)
mod.setting(
    "gpt_semantic_system_prompt",
    type=str,
    default=DEFAULT_SYSTEM_PROMPT,
    desc="System prompt used for model semantic translation",
)
