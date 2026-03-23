import judiagent.human_in_the_loop.cli as hitl_cli
import judiagent.human_in_the_loop.ui as hitl_ui
from judiagent.nodes.validation_review import (
    request_post_validation_review,
    request_pre_validation_review,
)


def test_request_pre_validation_review_uses_cli(monkeypatch):
    monkeypatch.setattr(
        hitl_cli,
        "response_on_check_code",
        lambda code: (True, "feedback", code + "\n# edited"),
    )

    decision = request_pre_validation_review("println(1)", cli_mode=True)

    assert decision.should_validate is True
    assert decision.user_response == "feedback"
    assert "# edited" in decision.working_code


def test_request_pre_validation_review_uses_ui(monkeypatch):
    monkeypatch.setattr(
        hitl_ui,
        "response_on_check_code",
        lambda code: (False, "", code),
    )

    decision = request_pre_validation_review("println(1)", cli_mode=False)

    assert decision.should_validate is False
    assert decision.user_response == ""
    assert decision.working_code == "println(1)"


def test_request_post_validation_review_uses_cli(monkeypatch):
    monkeypatch.setattr(
        hitl_cli,
        "response_on_error",
        lambda: (False, "skip"),
    )

    decision = request_post_validation_review(cli_mode=True)

    assert decision.should_fix is False
    assert decision.user_response == "skip"


def test_request_post_validation_review_uses_ui(monkeypatch):
    monkeypatch.setattr(
        hitl_ui,
        "response_on_error",
        lambda: (True, "retry"),
    )

    decision = request_post_validation_review(cli_mode=False)

    assert decision.should_fix is True
    assert decision.user_response == "retry"
