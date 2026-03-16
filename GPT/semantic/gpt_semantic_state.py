"""In-memory semantic state container.

Purpose:
- Stores pending plan, last confirmed plan, and last error for the current session.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py`
- `GPT/semantic/gpt_semantic_gui.py`
"""

from .gpt_semantic_types import GptSemanticPlan


class GptSemanticState:
    pending_request: str | None = None
    pending_plan: GptSemanticPlan | None = None
    pending_plan_json: str | None = None
    last_confirmed_plan: GptSemanticPlan | None = None
    last_confirmed_plan_json: str | None = None
    last_error: str | None = None

    @classmethod
    def set_pending(cls, request: str, plan: GptSemanticPlan, plan_json: str) -> None:
        cls.pending_request = request
        cls.pending_plan = plan
        cls.pending_plan_json = plan_json
        cls.last_error = None

    @classmethod
    def clear_pending(cls) -> None:
        cls.pending_request = None
        cls.pending_plan = None
        cls.pending_plan_json = None

    @classmethod
    def confirm_pending(cls) -> None:
        if cls.pending_plan is None or cls.pending_plan_json is None:
            return
        cls.last_confirmed_plan = cls.pending_plan
        cls.last_confirmed_plan_json = cls.pending_plan_json

    @classmethod
    def set_error(cls, message: str) -> None:
        cls.last_error = message
