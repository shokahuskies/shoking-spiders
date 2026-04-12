from typing import Dict, List, Tuple
import math
from ..agent import SwarmAgent
from ..task import Task

Vec2 = Tuple[float, float]

def dist(a: Vec2, b: Vec2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])

def bid(agent: SwarmAgent, task: Task) -> float:
    """
    Simple auction bid:
    Higher is better. We reward priority and penalize distance and low battery.
    """
    d = dist(agent.pos, task.location)
    battery_factor = agent.battery / 100.0
    return (10.0 * task.priority) - (d * 1.5) + (battery_factor * 2.0)

def allocate_auction(agents: List[SwarmAgent], tasks: List[Task]) -> Dict[int, int]:
    """
    Auction allocation:
    For each task, compute bids from all agents, then assign tasks to maximize bids.
    Simple greedy matching: pick highest bid pair, remove that agent and task, repeat.
    Returns mapping: agent_id -> task_id
    """
    open_tasks = [t for t in tasks if not t.completed]
    remaining_agents = {a.id: a for a in agents}
    remaining_tasks = {t.id: t for t in open_tasks}

    pairs: List[Tuple[float, int, int]] = []  # (score, agent_id, task_id)
    for a in agents:
        for t in open_tasks:
            pairs.append((bid(a, t), a.id, t.id))
    pairs.sort(reverse=True, key=lambda x: x[0])

    assignments: Dict[int, int] = {}
    for score, aid, tid in pairs:
        if aid in remaining_agents and tid in remaining_tasks:
            assignments[aid] = tid
            remaining_agents.pop(aid)
            remaining_tasks.pop(tid)
    return assignments
