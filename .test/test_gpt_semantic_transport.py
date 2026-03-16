import sys

sys.path.append(".")

from GPT.semantic import gpt_semantic_transport as transport


def test_routes_to_api(monkeypatch) -> None:
    calls: list[str] = []

    def fake_api(request, system_message, model):
        calls.append(f"api:{model}:{system_message}:{request['content'][0]['text']}")
        return {"type": "text", "text": "ok-api"}

    def fake_llm(*_args, **_kwargs):
        calls.append("llm")
        return {"type": "text", "text": "ok-llm"}

    monkeypatch.setattr(transport, "_model_endpoint", lambda: "https://example.com")
    monkeypatch.setattr(
        transport,
        "_helpers",
        lambda: {
            "resolve_model_name": lambda m: m,
            "format_message": lambda text: {"type": "text", "text": text},
            "extract_message": lambda resp: resp["text"],
            "send_request_to_api": fake_api,
            "send_request_to_llm_cli": fake_llm,
        },
    )

    result = transport.request_completion("sys", "user", "m", debug=False)
    assert result == "ok-api"
    assert calls[0].startswith("api:m:sys:user")


def test_routes_to_llm(monkeypatch) -> None:
    calls: list[str] = []

    def fake_api(*_args, **_kwargs):
        calls.append("api")
        return {"type": "text", "text": "ok-api"}

    def fake_llm(prompt, _content, system, model, _thread):
        calls.append(f"llm:{model}:{system}:{prompt['text']}")
        return {"type": "text", "text": "ok-llm"}

    monkeypatch.setattr(transport, "_model_endpoint", lambda: "llm")
    monkeypatch.setattr(
        transport,
        "_helpers",
        lambda: {
            "resolve_model_name": lambda m: f"resolved-{m}",
            "format_message": lambda text: {"type": "text", "text": text},
            "extract_message": lambda resp: resp["text"],
            "send_request_to_api": fake_api,
            "send_request_to_llm_cli": fake_llm,
        },
    )

    result = transport.request_completion("sys", "user", "m", debug=False)
    assert result == "ok-llm"
    assert calls[0].startswith("llm:resolved-m:sys:user")
