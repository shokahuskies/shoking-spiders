from typing import Dict, List, Optional, Tuple
import math
from ..agent import SwarmAgent
from ..task import Task

Vec2 = Tuple[float, float]

def dist(a: Vec2, b: Vec2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])

def allocate_greedy(agents: List[SwarmAgent], tasks: List[Task]) -> Dict[int, int]:
    """
    Greedy allocation:
    For each task (highest priority first), assign the closest available agent.
    Returns mapping: agent_id -> task_id
    """
    assignments: Dict[int, int] = {}
    free_agents = {a.id: a for a in agents}

    open_tasks = [t for t in tasks if not t.completed]
    open_tasks.sort(key=lambda t: -t.priority)

    for task in open_tasks:
        if not free_agents:
            break
        best_id: Optional[int] = None
        best_d = float("inf")
        for aid, agent in free_agents.items():
            d = dist(agent.pos, task.location)
            if d < best_d:
                best_d = d
                best_id = aid
        if best_id is not None:
            assignments[best_id] = task.id
            free_agents.pop(best_id)
    return assignments
