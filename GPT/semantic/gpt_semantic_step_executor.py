"""Internal step-by-step semantic executor.

Purpose:
- Executes parsed steps against Talon actions with synchronization and fallbacks.
- Raises a step-indexed error on the first failed action.

Called from:
- `GPT/semantic/gpt_semantic_executor.py`.
"""

from typing import Any

from .gpt_semantic_browser import call_focus_address, call_go_url
from .gpt_semantic_executor_helpers import (
    ARG_CALLS,
    NO_ARG_CALLS,
    is_running_app,
    launch_candidates,
    validate_running_app,
)
from .gpt_semantic_sync import settle_after_step, wait_for_app_focus
from .gpt_semantic_types import GptSemanticPlan, GptSemanticStep


class GptSemanticExecutionError(RuntimeError):
    def __init__(self, step_index: int, action_name: str, error: Exception):
        self.step_index = step_index
        self.action_name = action_name
        super().__init__(f"Step {step_index} ({action_name}) failed: {error}")


class GptSemanticStepExecutor:
    def __init__(self, runner: Any):
        self.runner = runner

    def run(self, plan: GptSemanticPlan) -> None:
        for index, step in enumerate(plan.steps, start=1):
            self._run_step(index, step)

    def _run_step(self, index: int, step: GptSemanticStep) -> None:
        try:
            self._dispatch(step)
            settle_after_step(step.action, self.runner)
        except Exception as exc:
            raise GptSemanticExecutionError(index, step.action, exc) from exc

    def _dispatch(self, step: GptSemanticStep) -> None:
        if self._dispatch_special(step):
            return
        if step.action in ARG_CALLS:
            return self._call_with_arg(step)
        self._call_no_arg(step)

    def _dispatch_special(self, step: GptSemanticStep) -> bool:
        if step.action == "sleep":
            self.runner.sleep(f"{step.args['ms']}ms")
            return True
        if step.action == "focus_address":
            call_focus_address(self.runner)
            return True
        if step.action == "switch_app":
            self._switch_app(str(step.args["app_name"]))
            return True
        if step.action == "launch_app":
            self._launch_app(str(step.args["app_name"]))
            return True
        return False

    def _switch_app(self, app_name: str) -> None:
        if not is_running_app(app_name):
            return self._launch_app(app_name)
        validate_running_app(app_name)
        self.runner.user.switcher_focus(app_name)
        wait_for_app_focus(self.runner, app_name)

    def _call_with_arg(self, step: GptSemanticStep) -> None:
        parent, method, arg_name = ARG_CALLS[step.action]
        value = step.args[arg_name]
        if step.action == "go_url":
            return call_go_url(self.runner, str(value))
        getattr(self._target(parent), method)(value)

    def _call_no_arg(self, step: GptSemanticStep) -> None:
        parent, method = NO_ARG_CALLS[step.action]
        getattr(self._target(parent), method)()

    def _target(self, parent: str | None) -> Any:
        return getattr(self.runner, parent) if parent else self.runner

    def _launch_app(self, app_name: str) -> None:
        last_error: Exception | None = None
        for candidate in launch_candidates(app_name):
            try:
                self.runner.user.switcher_launch(candidate)
                wait_for_app_focus(self.runner, app_name, candidate)
                return
            except Exception as exc:
                last_error = exc
        raise last_error or RuntimeError(f"Unable to launch app: '{app_name}'")
