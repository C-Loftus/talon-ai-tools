import sys

sys.path.append(".")

from GPT.semantic.gpt_semantic_guardrails import (
    GptSemanticGuardrailError,
    validate_guardrails,
)
from GPT.semantic.gpt_semantic_types import GptSemanticPlan, GptSemanticStep


def test_step_limit() -> None:
    plan = GptSemanticPlan([GptSemanticStep("new_tab", {}) for _ in range(2)])
    try:
        validate_guardrails(
            plan, max_steps=1, max_total_sleep_ms=2000, max_insert_chars=50
        )
        assert False
    except GptSemanticGuardrailError as exc:
        assert "maximum is 1" in str(exc)


def test_sleep_budget() -> None:
    plan = GptSemanticPlan([GptSemanticStep("sleep", {"ms": 3000})])
    try:
        validate_guardrails(
            plan, max_steps=5, max_total_sleep_ms=2000, max_insert_chars=50
        )
        assert False
    except GptSemanticGuardrailError as exc:
        assert "Total sleep is" in str(exc)


def test_insert_length() -> None:
    plan = GptSemanticPlan([GptSemanticStep("insert_text", {"text": "x" * 10})])
    try:
        validate_guardrails(
            plan, max_steps=5, max_total_sleep_ms=2000, max_insert_chars=5
        )
        assert False
    except GptSemanticGuardrailError as exc:
        assert "insert_text exceeds 5" in str(exc)


def test_blocked_combo() -> None:
    plan = GptSemanticPlan([GptSemanticStep("key", {"combo": "ctrl-w"})])
    try:
        validate_guardrails(
            plan, max_steps=5, max_total_sleep_ms=2000, max_insert_chars=50
        )
        assert False
    except GptSemanticGuardrailError as exc:
        assert "blocked" in str(exc)
