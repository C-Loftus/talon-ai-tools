"""Safety and limit checks for semantic plans.

Purpose:
- Validates plan size, sleep budget, text insert limits, and blocked key combos.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py` after parsing model output.
"""

from __future__ import annotations

from .gpt_semantic_types import GptSemanticPlan

BLOCKED_KEY_COMBOS = {
    "alt-f4",
    "ctrl-q",
    "cmd-q",
    "ctrl-w",
    "cmd-w",
    "super-l",
    "ctrl-alt-delete",
    "alt-space c",
}


class GptSemanticGuardrailError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_guardrails(
    plan: GptSemanticPlan,
    max_steps: int,
    max_total_sleep_ms: int,
    max_insert_chars: int,
) -> None:
    errors = _collect_errors(plan, max_steps, max_total_sleep_ms, max_insert_chars)
    if errors:
        raise GptSemanticGuardrailError(errors)


def _collect_errors(
    plan: GptSemanticPlan,
    max_steps: int,
    max_total_sleep_ms: int,
    max_insert_chars: int,
) -> list[str]:
    errors: list[str] = []
    if len(plan.steps) > max_steps:
        errors.append(f"Plan has {len(plan.steps)} steps; maximum is {max_steps}")
    _add_sleep_errors(plan, max_total_sleep_ms, errors)
    _add_insert_errors(plan, max_insert_chars, errors)
    _add_key_errors(plan, errors)
    return errors


def _add_sleep_errors(plan: GptSemanticPlan, max_total: int, errors: list[str]) -> None:
    total = sum(step.args.get("ms", 0) for step in plan.steps if step.action == "sleep")
    if total > max_total:
        errors.append(f"Total sleep is {total}ms; maximum is {max_total}ms")


def _add_insert_errors(
    plan: GptSemanticPlan, max_chars: int, errors: list[str]
) -> None:
    for index, step in enumerate(plan.steps, start=1):
        if step.action != "insert_text":
            continue
        if len(str(step.args.get("text", ""))) > max_chars:
            errors.append(f"Step {index}: insert_text exceeds {max_chars} characters")


def _add_key_errors(plan: GptSemanticPlan, errors: list[str]) -> None:
    for index, step in enumerate(plan.steps, start=1):
        if step.action != "key":
            continue
        combo = " ".join(str(step.args.get("combo", "")).strip().lower().split())
        if combo in BLOCKED_KEY_COMBOS:
            errors.append(f"Step {index}: key combo '{combo}' is blocked")
