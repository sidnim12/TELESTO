from biocontrolos.process.base import Action, ActionKind
from biocontrolos.safety import SafetyDecision, SafetyStatus


def test_actions_include_information_and_escalation_choices() -> None:
    assert {member.value for member in ActionKind} == {
        "control", "measure", "experiment", "simulate", "wait", "escalate"
    }


def test_safety_decision_can_require_human_approval() -> None:
    action = Action(kind=ActionKind.ESCALATE)
    decision = SafetyDecision(
        status=SafetyStatus.REQUIRE_HUMAN_APPROVAL,
        reason="uncertainty threshold exceeded",
        action=action,
    )
    assert decision.status is SafetyStatus.REQUIRE_HUMAN_APPROVAL
