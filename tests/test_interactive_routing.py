from types import SimpleNamespace

from acra.agents.planner import planner_agent as planner_module


def test_planner_routes_to_human_when_interactive_approval_required(monkeypatch):
    class FakePlannerChain:
        def invoke(self, inputs):
            return SimpleNamespace(
                tasks=["Confirm plan"],
                current_step="Confirm plan",
                workflow_status="planning",
                next_agent="coder",
                require_human_approval=True,
            )

    monkeypatch.setattr(
        planner_module,
        "create_planner_chain",
        lambda: FakePlannerChain(),
    )

    result = planner_module.planner_agent({
        "user_request": "build a script",
        "interactive": True,
    })

    assert result["next_agent"] == "human"


def test_planner_skips_human_route_without_interactive_flag(monkeypatch):
    class FakePlannerChain:
        def invoke(self, inputs):
            return SimpleNamespace(
                tasks=["Write code"],
                current_step="Write code",
                workflow_status="planning",
                next_agent="coder",
                require_human_approval=True,
            )

    monkeypatch.setattr(
        planner_module,
        "create_planner_chain",
        lambda: FakePlannerChain(),
    )

    result = planner_module.planner_agent({
        "user_request": "build a script",
        "interactive": False,
    })

    assert result["next_agent"] == "coder"
