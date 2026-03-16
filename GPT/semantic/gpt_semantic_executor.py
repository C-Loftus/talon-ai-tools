"""Semantic plan executor.

Purpose:
- Exposes the public execution API for semantic plans.
- Selects a Talon runner and delegates to the step executor implementation.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py` when running a confirmed plan.
"""

from typing import Any

try:
    from talon import actions as talon_actions
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    talon_actions = None

from .gpt_semantic_step_executor import (
    GptSemanticExecutionError,
    GptSemanticStepExecutor,
)
from .gpt_semantic_types import GptSemanticPlan


def execute_plan(plan: GptSemanticPlan, runner: Any = None) -> None:
    active_runner = runner if runner is not None else _default_runner()
    GptSemanticStepExecutor(active_runner).run(plan)


def _default_runner() -> Any:
    if talon_actions is None:
        raise RuntimeError("Talon actions are unavailable")
    return talon_actions
