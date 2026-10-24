"""
Subagents (Phase 11).

Task decomposition for complex multi-step goals. JARVIS spawns a subagent
with a specific goal and a scoped tool subset; the subagent works through
the task step by step and reports results back.

This is a structured task-delegation layer — the parent (JARVIS) still
executes all tools, but the subagent provides:

  * Goal isolation — each subagent has one clear objective
  * Tool scoping — only whitelisted tools are available to the subagent
  * Status tracking — pending / in-progress / completed / failed
  * Result aggregation — subagent output is stored and retrievable
  * Context separation — subagent context doesn't pollute the main prompt

All stdlib — no new dependencies.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SubagentStatus(Enum):
    PENDING = "pending"      # created, not yet started
    IN_PROGRESS = "in_progress"   # actively working
    COMPLETED = "completed"  # finished successfully
    FAILED = "failed"        # hit an error
    CANCELLED = "cancelled"  # stopped by user


@dataclass
class Subagent:
    """A subagent working on a specific goal with scoped tool access."""

    agent_id: str
    goal: str
    tools: list[str] = field(default_factory=list)   # whitelisted tool names
    status: SubagentStatus = SubagentStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    steps: list[dict] = field(default_factory=list)   # {"step": n, "action": "...", "result": "..."}
    max_steps: int = 10         # safety cap to prevent infinite loops


class SubagentManager:
    """Creates, tracks, and manages subagents."""

    def __init__(self):
        self._agents: dict[str, Subagent] = {}
        self._lock = __import__("threading").Lock()
        self._listeners: list = []

    def add_listener(self, cb) -> None:
        if callable(cb) and cb not in self._listeners:
            self._listeners.append(cb)

    def remove_listener(self, cb) -> None:
        if cb in self._listeners:
            self._listeners.remove(cb)

    def _notify(self) -> None:
        for cb in list(self._listeners):
            try:
                cb()
            except Exception:
                pass

    def spawn(self, goal: str, tools: Optional[list[str]] = None,
              max_steps: int = 10) -> str:
        """Create a new subagent. Returns the agent_id."""
        agent_id = f"sub-{uuid.uuid4().hex[:8]}"
        agent = Subagent(
            agent_id=agent_id,
            goal=goal,
            tools=tools or [],
            max_steps=max_steps,
        )
        with self._lock:
            self._agents[agent_id] = agent
        self._notify()
        return agent_id

    def get(self, agent_id: str) -> Optional[Subagent]:
        with self._lock:
            return self._agents.get(agent_id)

    def list(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "id": a.agent_id,
                    "goal": a.goal[:80] + ("…" if len(a.goal) > 80 else ""),
                    "status": a.status.value,
                    "tools": len(a.tools),
                    "steps": len(a.steps),
                    "created": a.created_at,
                }
                for a in self._agents.values()
            ]

    def list_detailed(self) -> list[dict]:
        """Rich worker records for the 3D World View & Activity Timeline."""
        now = time.time()
        with self._lock:
            out = []
            for a in self._agents.values():
                end_ts = (
                    a.updated_at
                    if a.status in (SubagentStatus.COMPLETED, SubagentStatus.FAILED, SubagentStatus.CANCELLED)
                    else now
                )
                out.append(
                    {
                        "id": a.agent_id,
                        "kind": "subagent",
                        "title": a.goal[:96] + ("…" if len(a.goal) > 96 else ""),
                        "goal": a.goal,
                        "status": a.status.value,
                        "tools": list(a.tools),
                        "steps": list(a.steps[-12:]),
                        "step_count": len(a.steps),
                        "max_steps": a.max_steps,
                        "result": (a.result or "")[:400] if a.result else None,
                        "error": (a.error or "")[:300] if a.error else None,
                        "created_at": a.created_at,
                        "updated_at": a.updated_at,
                        "elapsed_s": round(max(0.0, end_ts - a.created_at), 1),
                    }
                )
            return out

    def start(self, agent_id: str) -> bool:
        """Mark a subagent as in progress."""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent or agent.status != SubagentStatus.PENDING:
                return False
            agent.status = SubagentStatus.IN_PROGRESS
            agent.updated_at = time.time()
        self._notify()
        return True

    def add_step(self, agent_id: str, action: str, result: str) -> bool:
        """Record a step taken by the subagent."""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent or agent.status not in (
                    SubagentStatus.IN_PROGRESS, SubagentStatus.PENDING):
                return False
            if agent.status == SubagentStatus.PENDING:
                agent.status = SubagentStatus.IN_PROGRESS
            agent.steps.append({
                "step": len(agent.steps) + 1,
                "action": action,
                "result": result[:500],  # cap step result length
                "ts": time.time(),
            })
            agent.updated_at = time.time()
            if len(agent.steps) >= agent.max_steps:
                agent.status = SubagentStatus.COMPLETED
                agent.result = f"Subagent reached max_steps ({agent.max_steps}) without completion."
        self._notify()
        return True

    def complete(self, agent_id: str, result: str) -> bool:
        """Mark a subagent as completed with a result."""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent or agent.status not in (
                    SubagentStatus.IN_PROGRESS, SubagentStatus.PENDING):
                return False
            agent.status = SubagentStatus.COMPLETED
            agent.result = result
            agent.updated_at = time.time()
        self._notify()
        return True

    def fail(self, agent_id: str, error: str) -> bool:
        """Mark a subagent as failed."""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent or agent.status in (
                    SubagentStatus.COMPLETED, SubagentStatus.CANCELLED,
                    SubagentStatus.FAILED):
                return False
            agent.status = SubagentStatus.FAILED
            agent.error = error
            agent.updated_at = time.time()
        self._notify()
        return True

    def cancel(self, agent_id: str) -> bool:
        """Cancel a subagent."""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent or agent.status in (
                    SubagentStatus.COMPLETED, SubagentStatus.CANCELLED,
                    SubagentStatus.FAILED):
                return False
            agent.status = SubagentStatus.CANCELLED
            agent.updated_at = time.time()
        self._notify()
        return True

    def remove(self, agent_id: str) -> bool:
        """Remove a subagent from the registry (completed/failed only)."""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent or agent.status not in (
                    SubagentStatus.COMPLETED, SubagentStatus.FAILED,
                    SubagentStatus.CANCELLED):
                return False
            del self._agents[agent_id]
        self._notify()
        return True

    def clear_finished(self) -> int:
        """Remove all completed/failed/cancelled subagents. Returns count removed."""
        removed = 0
        with self._lock:
            done_ids = [
                aid
                for aid, a in self._agents.items()
                if a.status in (
                    SubagentStatus.COMPLETED,
                    SubagentStatus.FAILED,
                    SubagentStatus.CANCELLED,
                )
            ]
            for aid in done_ids:
                del self._agents[aid]
                removed += 1
        if removed:
            self._notify()
        return removed

    def count(self) -> int:
        with self._lock:
            return len(self._agents)


# ── Manager singleton ─────────────────────────────────────────────────────

_manager: Optional[SubagentManager] = None


def get_subagent_manager() -> SubagentManager:
    global _manager
    if _manager is None:
        _manager = SubagentManager()
    return _manager


# ── Tool declaration ─────────────────────────────────────────────────────

TOOL = {
    "name": "subagent",
    "description": (
        "Delegate complex multi-step tasks to a subagent. Use subagent when "
        "a task needs 5+ sequential steps, careful planning, or independent "
        "verification. Actions: 'spawn' (create a subagent with a goal and "
        "optional tool whitelist), 'list' (show all subagents), 'status' "
        "(check a subagent's progress), 'result' (get a completed subagent's "
        "output), 'cancel' (stop a subagent), 'remove' (delete a finished "
        "subagent). The parent (JARVIS) executes all tools — the subagent "
        "provides structure, goal tracking, and result isolation."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "spawn | list | status | result | cancel | remove",
            },
            "agent_id": {
                "type": "STRING",
                "description": "Subagent ID (from spawn) — required for status/result/cancel/remove",
            },
            "goal": {
                "type": "STRING",
                "description": "spawn: the goal/task for the subagent",
            },
            "tools": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "spawn: optional whitelist of tool names the subagent may use",
            },
            "max_steps": {
                "type": "INTEGER",
                "description": "spawn: maximum steps before auto-complete (default 10)",
            },
        },
        "required": ["action"],
    },
    "handler": None,  # set below
}


def subagent(parameters: dict, response=None, player=None,
             session_memory=None) -> str:
    """Handle subagent tool calls."""
    try:
        action = (parameters or {}).get("action", "").strip().lower()
        mgr = get_subagent_manager()

        if action == "spawn":
            goal = (parameters or {}).get("goal", "").strip()
            if not goal:
                return "subagent spawn: no goal provided."
            tools = (parameters or {}).get("tools")
            max_steps = int((parameters or {}).get("max_steps", 10))
            agent_id = mgr.spawn(goal, tools, max_steps)
            return (f"Subagent spawned: {agent_id}\n"
                    f"Goal: {goal}\n"
                    f"Tools: {', '.join(tools) if tools else 'all available'}\n"
                    f"Call subagent status agent_id={agent_id} to check progress.")

        elif action == "list":
            agents = mgr.list()
            if not agents:
                return "No subagents."
            lines = ["Subagents:"]
            for a in agents:
                lines.append(
                    f"  [{a['id']}] {a['status']} — {a['goal']} "
                    f"({a['steps']} steps, {a['tools']} tools)"
                )
            return "\n".join(lines)

        elif action == "status":
            agent_id = (parameters or {}).get("agent_id", "").strip()
            if not agent_id:
                return "subagent status: no agent_id provided."
            agent = mgr.get(agent_id)
            if not agent:
                return f"subagent status: agent '{agent_id}' not found."
            lines = [
                f"Subagent {agent_id}:",
                f"  Goal: {agent.goal}",
                f"  Status: {agent.status.value}",
                f"  Steps: {len(agent.steps)}/{agent.max_steps}",
                f"  Tools: {', '.join(agent.tools) if agent.tools else 'all'}",
            ]
            if agent.steps:
                lines.append("  Recent steps:")
                for s in agent.steps[-3:]:
                    lines.append(f"    {s['step']}. {s['action']} → {s['result'][:80]}")
            if agent.result:
                lines.append(f"  Result: {agent.result}")
            if agent.error:
                lines.append(f"  Error: {agent.error}")
            return "\n".join(lines)

        elif action == "result":
            agent_id = (parameters or {}).get("agent_id", "").strip()
            if not agent_id:
                return "subagent result: no agent_id provided."
            agent = mgr.get(agent_id)
            if not agent:
                return f"subagent result: agent '{agent_id}' not found."
            if agent.status != SubagentStatus.COMPLETED:
                return (f"subagent result: agent '{agent_id}' is "
                        f"{agent.status.value}, not completed yet.")
            return agent.result or "(no result recorded)"

        elif action == "cancel":
            agent_id = (parameters or {}).get("agent_id", "").strip()
            if not agent_id:
                return "subagent cancel: no agent_id provided."
            ok = mgr.cancel(agent_id)
            if ok:
                return f"Subagent {agent_id} cancelled."
            agent = mgr.get(agent_id)
            if not agent:
                return f"subagent cancel: agent '{agent_id}' not found."
            return f"subagent cancel: cannot cancel agent in {agent.status.value} state."

        elif action == "remove":
            agent_id = (parameters or {}).get("agent_id", "").strip()
            if not agent_id:
                return "subagent remove: no agent_id provided."
            ok = mgr.remove(agent_id)
            if ok:
                return f"Subagent {agent_id} removed."
            agent = mgr.get(agent_id)
            if not agent:
                return f"subagent remove: agent '{agent_id}' not found."
            return f"subagent remove: cannot remove agent in {agent.status.value} state."

        else:
            return (f"subagent: unknown action '{action}'. "
                    f"Use: spawn | list | status | result | cancel | remove")
    except Exception as e:
        return f"subagent: {e}"


TOOL["handler"] = subagent
