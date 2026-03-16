"""Strict JSON parser and schema validator for semantic plans.

Purpose:
- Parses model output into typed plan objects.
- Rejects unknown actions, bad args, and extra fields.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py` before guardrail validation.
"""

from __future__ import annotations

import json
from typing import Any

from .gpt_semantic_types import ACTION_ARG_SPECS, GptSemanticPlan, GptSemanticStep


class GptSemanticParseError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def parse_plan(raw_response: str) -> GptSemanticPlan:
    errors: list[str] = []
    payload = _load_json(raw_response, errors)
    if payload is None:
        raise GptSemanticParseError(errors)
    steps = _parse_steps(payload, errors)
    summary = payload.get("summary")
    if summary is not None and not isinstance(summary, str):
        errors.append("Root field 'summary' must be a string")
        summary = None
    if errors:
        raise GptSemanticParseError(errors)
    return GptSemanticPlan(steps=steps, summary=summary)


def _load_json(raw: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append(f"Response is not valid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append("Root must be an object")
        return None
    extras = sorted(set(payload) - {"steps", "summary"})
    if extras:
        errors.append(f"Root unsupported fields: {', '.join(extras)}")
    return payload


def _parse_steps(payload: dict[str, Any], errors: list[str]) -> list[GptSemanticStep]:
    raw_steps = payload.get("steps")
    if not isinstance(raw_steps, list):
        errors.append("Root field 'steps' must be a list")
        return []
    parsed = [_parse_step(i + 1, raw, errors) for i, raw in enumerate(raw_steps)]
    return [step for step in parsed if step]


def _parse_step(index: int, raw: Any, errors: list[str]) -> GptSemanticStep | None:
    if not isinstance(raw, dict):
        errors.append(f"Step {index}: must be an object")
        return None
    _validate_step_keys(index, raw, errors)
    action = raw.get("action")
    args = raw.get("args")
    if not isinstance(action, str):
        errors.append(f"Step {index}: 'action' must be a string")
        return None
    if action not in ACTION_ARG_SPECS:
        errors.append(f"Step {index}: unsupported action '{action}'")
        return None
    if not isinstance(args, dict):
        errors.append(f"Step {index}: 'args' must be an object")
        return None
    _validate_args(index, action, args, errors)
    return GptSemanticStep(action=action, args=args)


def _validate_step_keys(index: int, step: dict[str, Any], errors: list[str]) -> None:
    missing = sorted({"action", "args"} - set(step))
    extras = sorted(set(step) - {"action", "args"})
    if missing:
        errors.append(f"Step {index}: missing fields: {', '.join(missing)}")
    if extras:
        errors.append(f"Step {index}: unsupported fields: {', '.join(extras)}")


def _validate_args(
    index: int, action: str, args: dict[str, Any], errors: list[str]
) -> None:
    spec = ACTION_ARG_SPECS[action]
    missing = sorted(set(spec) - set(args))
    extras = sorted(set(args) - set(spec))
    if missing:
        errors.append(f"Step {index}: missing args: {', '.join(missing)}")
    if extras:
        errors.append(f"Step {index}: unsupported args: {', '.join(extras)}")
    for key, expected in spec.items():
        value = args.get(key)
        if value is not None and not _matches_type(value, expected):
            errors.append(f"Step {index}: arg '{key}' must be {expected.__name__}")


def _matches_type(value: Any, expected: type) -> bool:
    return not (expected is int and isinstance(value, bool)) and isinstance(
        value, expected
    )
