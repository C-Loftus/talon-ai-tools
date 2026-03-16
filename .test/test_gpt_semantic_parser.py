import sys

sys.path.append(".")

from GPT.semantic.gpt_semantic_parser import GptSemanticParseError, parse_plan


def test_parse_valid_plan() -> None:
    raw = (
        '{"steps":[{"action":"launch_app","args":{"app_name":"Text Editor"}},'
        '{"action":"go_url","args":{"url":"https://example.com"}}]}'
    )
    plan = parse_plan(raw)
    assert len(plan.steps) == 2
    assert plan.steps[0].args["app_name"] == "Text Editor"


def test_parse_malformed_json() -> None:
    try:
        parse_plan("{")
        assert False
    except GptSemanticParseError as exc:
        assert "not valid JSON" in str(exc)


def test_parse_unknown_action() -> None:
    raw = '{"steps":[{"action":"launch_missiles","args":{}}]}'
    try:
        parse_plan(raw)
        assert False
    except GptSemanticParseError as exc:
        assert "unsupported action" in str(exc)


def test_parse_bad_arg_type() -> None:
    raw = '{"steps":[{"action":"sleep","args":{"ms":"200"}}]}'
    try:
        parse_plan(raw)
        assert False
    except GptSemanticParseError as exc:
        assert "must be int" in str(exc)


def test_parse_rejects_extra_fields() -> None:
    raw = '{"steps":[{"action":"new_tab","args":{},"extra":true}],"garbage":1}'
    try:
        parse_plan(raw)
        assert False
    except GptSemanticParseError as exc:
        assert "unsupported" in str(exc)
