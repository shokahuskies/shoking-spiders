"""
coord_bridge.py
Bridges traj_avoid's MotionAgents (int ids) with multi-agent-sim's Coordinator
(string ids like "A0", "A1"). Handles assignment, goal sync, completion
detection, and event logging.

Assumes multi-agent-sim root is already on sys.path before this is imported.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from traj_avoid.agent import Agent as MotionAgent
from coordination.coordinator import Coordinator
from coordination.tasks import Task, TaskStatus


# ---------------------------------------------------------------------------
# EventLog
# ---------------------------------------------------------------------------

@dataclass
class EventLog:
    _entries: list[tuple[int, str, str]] = field(default_factory=list)

    def log(self, tick: int, event_type: str, detail: str) -> None:
        entry = (tick, event_type, detail)
        self._entries.append(entry)
        print(f"[tick={tick:>4}] {event_type:<8} {detail}")

    def dump(self) -> str:
        lines = [f"[tick={t:>4}] {et:<8} {d}" for t, et, d in self._entries]
        return "\n".join(lines)

    def entries(self) -> list[tuple[int, str, str]]:
        return list(self._entries)


# ---------------------------------------------------------------------------
# CoordBridge
# ---------------------------------------------------------------------------

@dataclass
class CoordBridge:
    """
    Bridges MotionAgent (int id) to Coordinator (string id "A{id}").

    Call step(tick) once per simulation tick, after motion physics have run,
    so that agent positions are current when checking goal arrival.
    """
    coordinator: Coordinator
    agents: List[MotionAgent]
    goal_tolerance: float
    log: EventLog = field(default_factory=EventLog)

    def __post_init__(self) -> None:
        # Log the designated leader once at init
        for a in self.agents:
            if self._str_id(a) == self.coordinator.leader_id:
                self.log.log(0, "LEADER",
                    f"agent id={a.id} ({self.coordinator.leader_id}) is the leader")
                break

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def step(self, tick: int) -> int:
        """
        Run one coordination tick. Returns the number of new assignments made.

        Order matters:
          1. Detect completions first so a worker is freed before reassignment.
          2. Assign idle workers.
          3. Sync goals for already-busy agents (guards against stale goals).
        """
        self._detect_completions(tick)
        new_assigns = self._assign_idle(tick)
        self._sync_goals()
        return new_assigns

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _str_id(agent: MotionAgent) -> str:
        return f"A{agent.id}"

    def _detect_completions(self, tick: int) -> None:
        for agent in self.agents:
            coord_id = self._str_id(agent)
            # Guard: only mark done if coordinator thinks this agent is busy.
            # Without this, at_goal stays True every tick after arrival and
            # complete_task would be called repeatedly.
            if coord_id not in self.coordinator.busy:
                continue
            if agent.at_goal(self.goal_tolerance):
                task = self.coordinator.complete_task(coord_id)
                if task is not None:
                    self.log.log(tick, "DONE",
                        f"{coord_id} completed {task.task_id} "
                        f"@ ({task.location[0]:.1f}, {task.location[1]:.1f})"
                        if task.location else f"{coord_id} completed {task.task_id}")

    def _assign_idle(self, tick: int) -> int:
        count = 0
        for agent in self.agents:
            coord_id = self._str_id(agent)
            task = self.coordinator.assign_direct(coord_id)
            if task is None:
                continue
            agent.goal = task.location if task.location is not None else agent.pos
            count += 1
            loc_str = (f"({task.location[0]:.1f}, {task.location[1]:.1f})"
                       if task.location else "no location")
            self.log.log(tick, "ASSIGN",
                f"{coord_id} -> {task.task_id} @ {loc_str}")
        return count

    def _sync_goals(self) -> None:
        """Ensure motion agent goals match their assigned task locations."""
        task_by_id = {t.task_id: t for t in self.coordinator.tasks}
        for agent in self.agents:
            coord_id = self._str_id(agent)
            task_id = self.coordinator.busy.get(coord_id)
            if task_id is None:
                continue
            task = task_by_id.get(task_id)
            if task is not None and task.location is not None:
                agent.goal = task.location
