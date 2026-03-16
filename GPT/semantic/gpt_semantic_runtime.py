"""Semantic runtime orchestration.

Purpose:
- Coordinates translation, parse/guardrail validation, preview state, and execution.
- Handles retry-on-parse-failure and user notifications.

Called from:
- `GPT/semantic/gpt_semantic_actions.py` action entry points.
"""

from talon import actions, clip, settings

from .gpt_semantic_context import semantic_context_text
from .gpt_semantic_executor import GptSemanticExecutionError, execute_plan
from .gpt_semantic_guardrails import validate_guardrails
from .gpt_semantic_gui import hide_preview, show_preview
from .gpt_semantic_parser import GptSemanticParseError, parse_plan
from .gpt_semantic_prompt import build_repair_prompt, build_user_prompt
from .gpt_semantic_state import GptSemanticState
from .gpt_semantic_transport import request_completion
from .gpt_semantic_types import GptSemanticPlan, plan_to_json


class GptSemanticRuntime:
    @staticmethod
    def generate(text: str, model: str) -> None:
        if not text.strip():
            return GptSemanticRuntime._notify("Semantic command is empty")
        try:
            count = GptSemanticRuntime._translate_and_store(text, model)
            GptSemanticRuntime._notify(f"Semantic plan ready: {count} steps")
        except Exception as exc:
            GptSemanticState.set_error(str(exc))
            GptSemanticRuntime._notify(f"Semantic planning failed: {exc}")

    @staticmethod
    def run_pending() -> None:
        plan = GptSemanticState.pending_plan
        if plan is None:
            return GptSemanticRuntime._notify("No semantic plan to run")
        try:
            execute_plan(plan)
            GptSemanticState.confirm_pending()
            GptSemanticState.clear_pending()
            hide_preview()
            GptSemanticRuntime._notify("Semantic plan completed")
        except GptSemanticExecutionError as exc:
            GptSemanticState.set_error(str(exc))
            GptSemanticRuntime._notify(f"Semantic execution failed: {exc}")

    @staticmethod
    def cancel_pending() -> None:
        hide_preview()
        GptSemanticState.clear_pending()
        GptSemanticRuntime._notify("Semantic plan canceled")

    @staticmethod
    def copy_pending() -> None:
        if not GptSemanticState.pending_plan_json:
            return GptSemanticRuntime._notify("No semantic plan to copy")
        clip.set_text(GptSemanticState.pending_plan_json)
        GptSemanticRuntime._notify("Semantic plan copied")

    @staticmethod
    def repeat_last() -> None:
        plan = GptSemanticState.last_confirmed_plan
        plan_json = GptSemanticState.last_confirmed_plan_json
        if plan is None or plan_json is None:
            return GptSemanticRuntime._notify("No last semantic plan to repeat")
        GptSemanticState.set_pending("Repeat last confirmed plan", plan, plan_json)
        show_preview()

    @staticmethod
    def _translate_and_store(text: str, model: str) -> int:
        plan = GptSemanticRuntime._translate_request(text, model)
        plan_json = plan_to_json(plan)
        GptSemanticState.set_pending(text, plan, plan_json)
        show_preview()
        return len(plan.steps)

    @staticmethod
    def _translate_request(text: str, model: str) -> GptSemanticPlan:
        debug = settings.get("user.gpt_semantic_debug")
        prompt = build_user_prompt(text, semantic_context_text(text))
        raw = request_completion(
            settings.get("user.gpt_semantic_system_prompt"), prompt, model, debug
        )
        try:
            return GptSemanticRuntime._parse_and_validate(raw)
        except GptSemanticParseError as exc:
            repair = build_repair_prompt(raw, exc.errors)
            fixed = request_completion(
                settings.get("user.gpt_semantic_system_prompt"), repair, model, debug
            )
            return GptSemanticRuntime._parse_and_validate(fixed)

    @staticmethod
    def _parse_and_validate(raw: str) -> GptSemanticPlan:
        plan = parse_plan(raw)
        validate_guardrails(
            plan,
            settings.get("user.gpt_semantic_max_steps"),
            settings.get("user.gpt_semantic_max_total_sleep_ms"),
            settings.get("user.gpt_semantic_max_insert_chars"),
        )
        return plan

    @staticmethod
    def _notify(message: str) -> None:
        actions.app.notify(message)
        if settings.get("user.gpt_semantic_debug"):
            print(message)
