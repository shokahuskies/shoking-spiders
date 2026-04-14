"""
integrated_demo.py
Integrates multi-agent-sim's Coordinator with traj_avoid's collision-avoiding
motion. The Coordinator (from multi-agent-sim) assigns tasks to agents; traj_avoid
handles physical movement and collision avoidance.

Run from the traj-planning/ directory:
    python integrated_demo.py
"""
from __future__ import annotations

import os
import sys
import random

# ---------------------------------------------------------------------------
# sys.path — must happen before any cross-project imports
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_MULTI_AGENT_ROOT = os.path.normpath(os.path.join(_HERE, "..", "multi-agent-sim"))

for _p in (_MULTI_AGENT_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# traj_avoid imports (same project)
# ---------------------------------------------------------------------------
from traj_avoid.config import Config as MotionConfig
from traj_avoid.agent import Agent as MotionAgent
from traj_avoid.sim import tick as motion_tick
from traj_avoid.viz import animate

# ---------------------------------------------------------------------------
# multi-agent-sim imports (cross-project)
# ---------------------------------------------------------------------------
from coordination.coordinator import Coordinator
from coordination.tasks import Task, TaskStatus

# ---------------------------------------------------------------------------
# Bridge (same project)
# ---------------------------------------------------------------------------
from coord_bridge import CoordBridge


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_tasks(n: int, x_max: float, y_max: float, rng: random.Random) -> list[Task]:
    return [
        Task(
            task_id=f"T{i}",
            work_ticks=1,  # completion driven by physical arrival, not a timer
            location=(
                rng.uniform(1.0, x_max - 1.0),
                rng.uniform(1.0, y_max - 1.0),
            ),
        )
        for i in range(n)
    ]


def make_agents(n: int, cfg: MotionConfig, rng: random.Random) -> list[MotionAgent]:
    agents = []
    for i in range(n):
        pos = (
            rng.uniform(cfg.x_min + 1.0, cfg.x_max - 1.0),
            rng.uniform(cfg.y_min + 1.0, cfg.y_max - 1.0),
        )
        agents.append(MotionAgent(
            id=i,
            pos=pos,
            vel=(0.0, 0.0),
            goal=pos,  # park in place until the coordinator assigns a task
            radius=cfg.agent_radius,
            max_speed=cfg.max_speed,
        ))
    return agents


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    N_AGENTS = 6
    N_TASKS  = 10

    rng = random.Random()  # seeded from system clock — different each run
    motion_cfg = MotionConfig()

    tasks         = make_tasks(N_TASKS, motion_cfg.x_max, motion_cfg.y_max, rng)
    motion_agents = make_agents(N_AGENTS, motion_cfg, rng)

    # Leader is always "A0" (maps to MotionAgent id=0)
    coordinator = Coordinator(leader_id="A0", tasks=tasks)
    bridge = CoordBridge(
        coordinator=coordinator,
        agents=motion_agents,
        goal_tolerance=motion_cfg.goal_tolerance,
    )

    print(f"Leader  : {coordinator.leader_id}")
    print(f"Agents  : {[f'A{a.id}' for a in motion_agents]}")
    print(f"Tasks   : {[t.task_id for t in tasks]}")
    print("-" * 50)

    # Initial assignment before the first frame
    bridge.step(0)

    tick_state = {"k": 0}

    def integrated_tick(_agents, _cfg):
        result = motion_tick(motion_agents, motion_cfg)
        tick_state["k"] += 1
        bridge.step(tick_state["k"])
        return result

    animate(motion_agents, tick_fn=integrated_tick, cfg=motion_cfg)

    # ------------------------------------------------------------------
    # Summary (printed after the window closes)
    # ------------------------------------------------------------------
    total  = len(coordinator.tasks)
    done   = sum(1 for t in coordinator.tasks if t.status == TaskStatus.DONE)
    assign = sum(1 for t in coordinator.tasks if t.status == TaskStatus.ASSIGNED)
    pend   = sum(1 for t in coordinator.tasks if t.status == TaskStatus.PENDING)

    print("\n" + "=" * 50)
    print("SIMULATION COMPLETE")
    print("=" * 50)
    print(f"  Ticks run  : {tick_state['k']}")
    print(f"  DONE       : {done}/{total}")
    print(f"  ASSIGNED   : {assign}")
    print(f"  PENDING    : {pend}")
    print("\nFull event log:")
    print(bridge.log.dump() or "  (no events)")
    print("=" * 50)


if __name__ == "__main__":
    main()
