"""Shared semantic schema types and constants.

Purpose:
- Defines allowed actions, typed plan/step data structures, and JSON serialization helpers.

Called from:
- Parser, guardrails, runtime, executor, and prompt modules.
"""

import json
from dataclasses import dataclass
from typing import Any

ActionArgSpecs = dict[str, dict[str, type]]

ACTION_ARG_SPECS: ActionArgSpecs = {
    "switch_app": {"app_name": str},
    "launch_app": {"app_name": str},
    "focus_address": {},
    "new_tab": {},
    "go_url": {"url": str},
    "find_text": {"text": str},
    "insert_text": {"text": str},
    "key": {"combo": str},
    "sleep": {"ms": int},
    "copy": {},
    "paste": {},
    "select_all": {},
    "undo": {},
    "redo": {},
    "line_start": {},
    "line_end": {},
    "delete_selection": {},
}

ALLOWED_ACTIONS: tuple[str, ...] = tuple(ACTION_ARG_SPECS.keys())


@dataclass(frozen=True)
class GptSemanticStep:
    action: str
    args: dict[str, Any]


@dataclass(frozen=True)
class GptSemanticPlan:
    steps: list[GptSemanticStep]
    summary: str | None = None


def plan_to_dict(plan: GptSemanticPlan) -> dict[str, Any]:
    payload = {"steps": [vars(step) for step in plan.steps]}
    if plan.summary:
        payload["summary"] = plan.summary
    return payload


def plan_to_json(plan: GptSemanticPlan) -> str:
    return json.dumps(plan_to_dict(plan), indent=2)
