"""Tests — subagents (Phase 11): task decomposition with scoped tool access."""
from core.subagents import (
    Subagent, SubagentManager, SubagentStatus, get_subagent_manager,
    subagent, TOOL,
)


# ── Subagent dataclass ────────────────────────────────────────────────────

def test_subagent_defaults():
    s = Subagent(agent_id="sub-123", goal="Test goal")
    assert s.agent_id == "sub-123"
    assert s.goal == "Test goal"
    s.tools.append("send_message")
    assert s.tools == ["send_message"]
    assert s.status == SubagentStatus.PENDING
    assert s.result is None
    assert s.error is None
    assert s.steps == []
    assert s.max_steps == 10


def test_subagent_status_enum():
    assert SubagentStatus.PENDING.value == "pending"
    assert SubagentStatus.IN_PROGRESS.value == "in_progress"
    assert SubagentStatus.COMPLETED.value == "completed"
    assert SubagentStatus.FAILED.value == "failed"
    assert SubagentStatus.CANCELLED.value == "cancelled"


# ── SubagentManager ───────────────────────────────────────────────────────

def test_manager_spawn_and_get():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Research Python")
    agent = mgr.get(agent_id)
    assert agent is not None
    assert agent.goal == "Research Python"
    assert agent.status == SubagentStatus.PENDING


def test_manager_list():
    mgr = SubagentManager()
    mgr.spawn("Task A")
    mgr.spawn("Task B")
    agents = mgr.list()
    assert len(agents) == 2
    ids = {a["id"] for a in agents}
    assert all("sub-" in i for i in ids)


def test_manager_start():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Task A")
    assert mgr.start(agent_id) is True
    assert mgr.get(agent_id).status == SubagentStatus.IN_PROGRESS


def test_manager_add_step():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Task A")
    mgr.start(agent_id)
    assert mgr.add_step(agent_id, "search web", "found results") is True
    agent = mgr.get(agent_id)
    assert len(agent.steps) == 1
    assert agent.steps[0]["action"] == "search web"
    assert agent.status == SubagentStatus.IN_PROGRESS


def test_manager_complete_and_result():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Task A")
    assert mgr.complete(agent_id, "Done!") is True
    agent = mgr.get(agent_id)
    assert agent.status == SubagentStatus.COMPLETED
    assert agent.result == "Done!"


def test_manager_fail():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Task A")
    assert mgr.fail(agent_id, "Oops") is True
    agent = mgr.get(agent_id)
    assert agent.status == SubagentStatus.FAILED
    assert agent.error == "Oops"


def test_manager_cancel():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Task A")
    assert mgr.cancel(agent_id) is True
    assert mgr.get(agent_id).status == SubagentStatus.CANCELLED


def test_manager_remove_completed():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Task A")
    mgr.complete(agent_id, "Done")
    assert mgr.remove(agent_id) is True
    assert mgr.get(agent_id) is None


def test_manager_remove_in_progress_fails():
    mgr = SubagentManager()
    agent_id = mgr.spawn("Task A")
    mgr.start(agent_id)
    assert mgr.remove(agent_id) is False
    assert mgr.get(agent_id) is not None


def test_manager_singleton():
    m1 = get_subagent_manager()
    m2 = get_subagent_manager()
    assert m1 is m2


# ── Tool declaration ──────────────────────────────────────────────────────

def test_tool_declaration():
    assert TOOL["name"] == "subagent"
    assert TOOL["handler"] is subagent
    assert "spawn" in TOOL["description"]
    assert "list" in TOOL["description"]
    assert "status" in TOOL["description"]
    assert "result" in TOOL["description"]
    assert "cancel" in TOOL["description"]
    assert "remove" in TOOL["description"]
    assert TOOL["parameters"]["required"] == ["action"]
    props = TOOL["parameters"]["properties"]
    for key in ("action", "agent_id", "goal", "tools", "max_steps"):
        assert key in props


# ── Tool actions ──────────────────────────────────────────────────────────

def test_spawn():
    result = subagent({"action": "spawn", "goal": "Research Python",
                       "tools": ["web_search"], "max_steps": 5})
    assert "Subagent spawned:" in result
    assert "Research Python" in result
    assert "web_search" in result


def test_spawn_no_goal():
    result = subagent({"action": "spawn"})
    assert "no goal provided" in result.lower()


def test_list_empty():
    # Use a fresh manager by temporarily resetting singleton
    import core.subagents as sm
    sm._manager = SubagentManager()
    try:
        result = subagent({"action": "list"})
        assert result == "No subagents."
    finally:
        sm._manager = None  # allow fresh singleton next time


def test_list_with_subagent():
    import core.subagents as sm
    sm._manager = SubagentManager()
    try:
        subagent({"action": "spawn", "goal": "Task A"})
        result = subagent({"action": "list"})
        assert "Task A" in result
    finally:
        sm._manager = None


def test_status_unknown_agent():
    import core.subagents as sm
    sm._manager = SubagentManager()
    try:
        result = subagent({"action": "status", "agent_id": "sub-nonexistent"})
        assert "not found" in result.lower()
    finally:
        sm._manager = None


def test_status_agent():
    import core.subagents as sm
    sm._manager = SubagentManager()
    try:
        res = subagent({"action": "spawn", "goal": "Task A", "max_steps": 3})
        agent_id = res.split(":")[1].strip().split("\n")[0]
        result = subagent({"action": "status", "agent_id": agent_id})
        assert "Pending" in result or "pending" in result
        assert "Task A" in result
    finally:
        sm._manager = None


def test_result_before_complete():
    import core.subagents as sm
    sm._manager = SubagentManager()
    try:
        res = subagent({"action": "spawn", "goal": "Task A"})
        agent_id = res.split(":")[1].strip().split("\n")[0]
        result = subagent({"action": "result", "agent_id": agent_id})
        assert "not completed" in result.lower()
    finally:
        sm._manager = None


def test_result_after_complete():
    import core.subagents as sm
    sm._manager = SubagentManager()
    try:
        res = subagent({"action": "spawn", "goal": "Task A"})
        agent_id = res.split(":")[1].strip().split("\n")[0]
        mgr = get_subagent_manager()
        mgr.complete(agent_id, "All done!")
        result = subagent({"action": "result", "agent_id": agent_id})
        assert result == "All done!"
    finally:
        sm._manager = None


def test_unknown_action():
    result = subagent({"action": "bogus"})
    assert "unknown action" in result.lower()
