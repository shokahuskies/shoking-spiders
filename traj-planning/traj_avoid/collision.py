from typing import Dict, List, Tuple
from .agent import Agent, add, mul, sub, norm

Vec2 = Tuple[float, float]

def predict_positions(agent: Agent, dt: float, horizon_steps: int) -> List[Vec2]:
    return [add(agent.pos, mul(agent.vel, dt * k)) for k in range(horizon_steps + 1)]

def predict_all(agents: List[Agent], dt: float, horizon_steps: int) -> Dict[int, List[Vec2]]:
    return {a.id: predict_positions(a, dt, horizon_steps) for a in agents}

def will_conflict(pred_a: List[Vec2], pred_b: List[Vec2], min_dist: float) -> bool:
    steps = min(len(pred_a), len(pred_b))
    for k in range(steps):
        if norm(sub(pred_a[k], pred_b[k])) < min_dist:
            return True
    return False

def find_conflicts(agents: List[Agent], preds: Dict[int, List[Vec2]], min_dist: float) -> List[Tuple[int, int]]:
    conflicts: List[Tuple[int, int]] = []
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            a, b = agents[i], agents[j]
            if will_conflict(preds[a.id], preds[b.id], min_dist):
                lo, hi = (a.id, b.id) if a.id < b.id else (b.id, a.id)
                conflicts.append((lo, hi))
    return conflicts

def actual_collision(a: Agent, b: Agent, min_dist: float) -> bool:
    return norm(sub(a.pos, b.pos)) < min_dist
