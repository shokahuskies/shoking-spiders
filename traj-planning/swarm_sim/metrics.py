from typing import List
from .agent import SwarmAgent
from .task import Task

def summarize(agents: List[SwarmAgent], tasks: List[Task]) -> str:
    done = sum(1 for t in tasks if t.completed)
    open_ = sum(1 for t in tasks if not t.completed)
    avg_batt = sum(a.battery for a in agents) / max(1, len(agents))
    assigned = sum(1 for t in tasks if t.assigned_to is not None and not t.completed)
    return f"tasks_done={done} tasks_open={open_} tasks_assigned={assigned} avg_battery={avg_batt:.1f}"
