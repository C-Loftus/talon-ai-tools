"""Prompt builders for semantic planning and one-shot repair.

Purpose:
- Defines default system prompt, schema text, and rules for model outputs.
- Builds initial and repair prompts with runtime context.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py` during plan generation.
"""

from .gpt_semantic_types import ACTION_ARG_SPECS, ALLOWED_ACTIONS

DEFAULT_SYSTEM_PROMPT = (
    "You translate natural-language desktop requests into a strictly valid JSON action plan. "
    "Return only JSON. Never include markdown, prose, or code fences. "
    "Use only non-destructive actions and prefer the smallest plan that satisfies the request."
)


def build_schema_text() -> str:
    lines = ['{"steps":[{"action":"...", "args":{...}}], "summary":"optional"}']
    lines.extend(f"- {name}({', '.join(_arg_parts(name))})" for name in ALLOWED_ACTIONS)
    return "\n".join(lines)


def build_user_prompt(request_text: str, active_context: str) -> str:
    parts = [
        f"Active context:\n{active_context}",
        f"Allowed schema:\n{build_schema_text()}",
        _rules_text(),
        f'User request:\n"{request_text}"',
    ]
    return "\n\n".join(parts)


def build_repair_prompt(previous_response: str, errors: list[str]) -> str:
    error_lines = "\n".join(f"- {error}" for error in errors)
    parts = [
        "Your last response failed schema validation.",
        f"Validation errors:\n{error_lines}",
        f"Previous response:\n{previous_response}",
        "Return corrected JSON only.",
    ]
    return "\n\n".join(parts)


def _arg_parts(action: str) -> list[str]:
    spec = ACTION_ARG_SPECS[action]
    return [f"{key}:{kind.__name__}" for key, kind in spec.items()]


def _rules_text() -> str:
    lines = [
        "Rules:",
        "- Root keys allowed: steps, summary",
        "- Step keys allowed: action, args",
        "- No destructive/system power/quit/close shortcuts",
        "- switch_app must use app names listed in running apps context",
        "- launch_app.args.app_name must be exactly one command from launchable apps context",
        "- Use executable commands from context, not capitalized product names",
        "- If a requested app name is colloquial, map it to the closest launchable command by function",
        "- Keep steps concise and deterministic",
    ]
    return "\n".join(lines)
