"""Model transport adapter for semantic planning.

Purpose:
- Reuses talon-ai-tools model helper functions for API/LLM CLI routing.
- Returns normalized assistant message text to the semantic runtime.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py` during translation and repair retry.
"""

from __future__ import annotations

from typing import Any


class GptSemanticTransportError(RuntimeError):
    pass


def request_completion(
    system_prompt: str, user_prompt: str, model: str, debug: bool
) -> str:
    helpers = _helpers()
    model_name = helpers["resolve_model_name"](model)
    endpoint = _model_endpoint()
    prompt = helpers["format_message"](user_prompt)
    if debug:
        print({"gpt_semantic_model": model_name, "endpoint": endpoint})
    if endpoint == "llm":
        response = helpers["send_request_to_llm_cli"](
            prompt, None, system_prompt, model_name, False
        )
    else:
        request = {"role": "user", "content": [prompt]}
        response = helpers["send_request_to_api"](request, system_prompt, model_name)
    return helpers["extract_message"](response)


def _helpers() -> dict[str, Any]:
    try:
        from ...lib.modelHelpers import (
            extract_message,
            format_message,
            resolve_model_name,
            send_request_to_api,
            send_request_to_llm_cli,
        )
    except ImportError:
        from lib.modelHelpers import (
            extract_message,
            format_message,
            resolve_model_name,
            send_request_to_api,
            send_request_to_llm_cli,
        )
    return {
        "extract_message": extract_message,
        "format_message": format_message,
        "resolve_model_name": resolve_model_name,
        "send_request_to_api": send_request_to_api,
        "send_request_to_llm_cli": send_request_to_llm_cli,
    }


def _model_endpoint() -> str:
    try:
        from talon import settings
    except ImportError as exc:  # pragma: no cover
        raise GptSemanticTransportError("Talon settings are unavailable") from exc
    endpoint = settings.get("user.model_endpoint")
    if not isinstance(endpoint, str) or not endpoint:
        raise GptSemanticTransportError("Setting user.model_endpoint is missing")
    return endpoint
