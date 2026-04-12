import math
from typing import Dict, List, Tuple, Optional
from ..agent import Agent, add, mul, sub, norm, unit

Vec2 = Tuple[float, float]

def headings(num: int) -> List[Vec2]:
    dirs: List[Vec2] = []
    for i in range(num):
        ang = (2.0 * math.pi * i) / num
        dirs.append((math.cos(ang), math.sin(ang)))
    return dirs

def danger_penalty(next_pos: Vec2, other_preds: Dict[int, List[Vec2]], min_dist: float) -> float:
    penalty = 0.0
    for preds in other_preds.values():
        for p in preds:
            d = norm(sub(next_pos, p))
            if d < min_dist:
                penalty += (min_dist - d) ** 2 * 10.0
                break
    return penalty

def greedy_replan_velocity(
    agent: Agent,
    dt: float,
    other_preds: Dict[int, List[Vec2]],
    min_dist: float,
    num_headings: int,
    slow_factor: float,
    stop_allowed: bool,
    alpha_goal: float,
    beta_danger: float,
) -> Optional[Vec2]:
    cand_dirs = headings(num_headings)
    cand_speeds = [agent.max_speed, agent.max_speed * slow_factor]

    if stop_allowed:
        cand_dirs = cand_dirs + [(0.0, 0.0)]
        cand_speeds = cand_speeds + [0.0]

    best_cost = float("inf")
    best_vel: Optional[Vec2] = None

    for d in cand_dirs:
        for spd in cand_speeds:
            vel = mul(unit(d), spd) if spd > 0 else (0.0, 0.0)
            next_pos = add(agent.pos, mul(vel, dt))

            c_goal = norm(sub(agent.goal, next_pos))
            c_danger = danger_penalty(next_pos, other_preds, min_dist)
            cost = alpha_goal * c_goal + beta_danger * c_danger

            if cost < best_cost:
                best_cost = cost
                best_vel = vel

    return best_vel
