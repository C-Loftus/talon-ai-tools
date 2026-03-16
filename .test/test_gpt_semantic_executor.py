"""Executor behavior tests for GPT semantic commands.

Purpose:
- Verifies action mapping, browser fallback behavior, synchronization hooks, and stop-on-error policy.

Called from:
- Pytest suite in `user/talon-ai-tools/.test`.
"""

import sys

sys.path.append(".")

from GPT.semantic import gpt_semantic_executor_helpers as helpers
from GPT.semantic import gpt_semantic_step_executor as step_executor
from GPT.semantic.gpt_semantic_executor import GptSemanticExecutionError, execute_plan
from GPT.semantic.gpt_semantic_types import GptSemanticPlan, GptSemanticStep


class Proxy:
    def __init__(self, runner: "FakeRunner", prefix: str):
        self._runner = runner
        self._prefix = prefix

    def __getattr__(self, name: str):
        def call(*args):
            self._runner.record(f"{self._prefix}.{name}", *args)

        return call


class FakeRunner:
    def __init__(self, fail_call: str | None = None, fail_message: str = "boom"):
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.fail_call = fail_call
        self.fail_message = fail_message
        self.user = Proxy(self, "user")
        self.browser = Proxy(self, "browser")
        self.app = Proxy(self, "app")
        self.edit = Proxy(self, "edit")

    def record(self, name: str, *args) -> None:
        self.calls.append((name, args))
        if name == self.fail_call:
            raise RuntimeError(self.fail_message)

    def insert(self, text: str) -> None:
        self.record("insert", text)

    def key(self, combo: str) -> None:
        self.record("key", combo)

    def sleep(self, value: str) -> None:
        self.record("sleep", value)


def test_mapping_includes_launch_app(monkeypatch) -> None:
    monkeypatch.setattr(helpers, "resolve_launch_command", lambda _name: "text-editor")
    plan = GptSemanticPlan(
        steps=[
            GptSemanticStep("launch_app", {"app_name": "Text Editor"}),
            GptSemanticStep("new_tab", {}),
        ]
    )
    runner = FakeRunner()
    execute_plan(plan, runner=runner)
    assert runner.calls[0] == ("user.switcher_launch", ("text-editor",))
    assert runner.calls[1] == ("app.tab_open", ())


def test_launch_app_uses_resolved_command(monkeypatch) -> None:
    monkeypatch.setattr(
        helpers, "resolve_launch_command", lambda _name: "gnome-text-editor"
    )
    plan = GptSemanticPlan([GptSemanticStep("launch_app", {"app_name": "Gedit"})])
    runner = FakeRunner()
    execute_plan(plan, runner=runner)
    assert runner.calls[0] == ("user.switcher_launch", ("gnome-text-editor",))


def test_stop_on_first_error() -> None:
    plan = GptSemanticPlan(
        [GptSemanticStep("new_tab", {}), GptSemanticStep("copy", {})]
    )
    runner = FakeRunner(fail_call="app.tab_open")
    try:
        execute_plan(plan, runner=runner)
        assert False
    except GptSemanticExecutionError as exc:
        assert "Step 1 (new_tab)" in str(exc)
    assert len(runner.calls) == 1


def test_browser_fallbacks() -> None:
    msg = "Action 'browser.go' exists but the Module method is empty and no Context reimplements it"
    runner = FakeRunner(fail_call="browser.go", fail_message=msg)
    execute_plan(
        GptSemanticPlan([GptSemanticStep("go_url", {"url": "https://x"})]), runner
    )
    assert ("key", ("ctrl-l",)) in runner.calls
    assert ("insert", ("https://x",)) in runner.calls


def test_switch_app_waits_for_focus(monkeypatch) -> None:
    waits: list[tuple[str, str | None]] = []
    monkeypatch.setattr(
        step_executor, "wait_for_app_focus", lambda _r, n, c=None: waits.append((n, c))
    )
    plan = GptSemanticPlan(
        [GptSemanticStep("switch_app", {"app_name": "Google Chrome"})]
    )
    runner = FakeRunner()
    execute_plan(plan, runner=runner)
    assert runner.calls[0] == ("user.switcher_focus", ("Google Chrome",))
    assert waits == [("Google Chrome", None)]


def test_execute_plan_applies_settle_after_each_step(monkeypatch) -> None:
    settled: list[str] = []
    monkeypatch.setattr(
        step_executor, "settle_after_step", lambda action, _r: settled.append(action)
    )
    plan = GptSemanticPlan(
        [GptSemanticStep("new_tab", {}), GptSemanticStep("copy", {})]
    )
    execute_plan(plan, runner=FakeRunner())
    assert settled == ["new_tab", "copy"]


def test_switch_app_falls_back_to_launch_if_not_running(monkeypatch) -> None:
    waits: list[tuple[str, str | None]] = []
    monkeypatch.setattr(step_executor, "is_running_app", lambda _name: False)
    monkeypatch.setattr(
        step_executor, "launch_candidates", lambda _name: ["google-chrome"]
    )
    monkeypatch.setattr(
        step_executor, "wait_for_app_focus", lambda _r, n, c=None: waits.append((n, c))
    )
    plan = GptSemanticPlan(
        [GptSemanticStep("switch_app", {"app_name": "Google Chrome"})]
    )
    runner = FakeRunner()
    execute_plan(plan, runner=runner)
    assert runner.calls[0] == ("user.switcher_launch", ("google-chrome",))
    assert waits == [("Google Chrome", "google-chrome")]
