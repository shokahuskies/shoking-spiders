from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import random
import math

from .config import SwarmConfig
from .agent import SwarmAgent
from .task import Task

Vec2 = Tuple[float, float]

def dist(a: Vec2, b: Vec2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])

@dataclass
class World:
    cfg: SwarmConfig
    agents: List[SwarmAgent]
    tasks: List[Task]
    tick: int = 0

    @staticmethod
    def random_world(cfg: SwarmConfig, n_agents: int, seed: int | None = None) -> "World":
        rng = random.Random(seed)
        agents = []
        for i in range(n_agents):
            agents.append(SwarmAgent(
                id=i,
                pos=(rng.uniform(0, cfg.world_w), rng.uniform(0, cfg.world_h)),
                battery=cfg.battery_max
            ))
        tasks = []
        for t in range(cfg.initial_tasks):
            tasks.append(Task(
                id=t,
                location=(rng.uniform(0, cfg.world_w), rng.uniform(0, cfg.world_h)),
                priority=rng.choice([1, 1, 2, 3])  # mostly 1, some higher
            ))
        return World(cfg=cfg, agents=agents, tasks=tasks)

    def apply_assignments(self, assignments: Dict[int, int]) -> None:
        task_by_id = {t.id: t for t in self.tasks}
        agent_by_id = {a.id: a for a in self.agents}

        for aid, tid in assignments.items():
            if tid not in task_by_id or aid not in agent_by_id:
                continue
            agent = agent_by_id[aid]
            if agent.current_task_id is not None:
                continue  # already assigned — don't yank mid-flight
            task = task_by_id[tid]
            task.assigned_to = aid
            agent.goal = task.location
            agent.current_task_id = tid

    def step_high_level(self) -> None:
        """
        High-level tick:
        - advances time
        - marks tasks complete if agent is "at task"
        - drains battery based on a fake movement model (for allocation realism)
        NOTE: This world does NOT do motion/collision. Integration will.
        """
        self.tick += 1
        task_by_id = {t.id: t for t in self.tasks}

        for a in self.agents:
            # If agent has a goal, pretend it moved a small amount toward it (for high-level bookkeeping)
            if a.goal is not None and a.battery > 0:
                # fake movement distance budget per high-level tick
                step_dist = 0.8
                # battery drain based on "distance moved"
                a.battery = max(0.0, a.battery - self.cfg.battery_drain_per_unit * step_dist)

                # if "close enough", complete task
                if dist(a.pos, a.goal) < 0.8:
                    if a.current_task_id is not None and a.current_task_id in task_by_id:
                        task_by_id[a.current_task_id].completed = True
                    a.goal = None
                    a.current_task_id = None
