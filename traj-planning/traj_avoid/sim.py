from typing import Dict, List, Tuple
from .agent import Agent, sub, norm, mul
from .collision import predict_all, find_conflicts, actual_collision
from .path_planning.greedy import greedy_replan_velocity
from .path_planning.astar import world_to_cell, cell_to_world, build_unsafe_cells, astar_path

Vec2 = Tuple[float, float]

def clamp(pos: Vec2, cfg) -> Vec2:
    return (min(max(pos[0], cfg.x_min), cfg.x_max), min(max(pos[1], cfg.y_min), cfg.y_max))

def _other_preds(preds: Dict[int, List[Vec2]], exclude: int) -> Dict[int, List[Vec2]]:
    return {aid: p for aid, p in preds.items() if aid != exclude}

def choose_velocity(agent: Agent, preds: Dict[int, List[Vec2]], cfg) -> Vec2:
    min_dist = (cfg.agent_radius * 2.0) + cfg.safety_margin
    other = _other_preds(preds, agent.id)

    v = greedy_replan_velocity(
        agent=agent,
        dt=cfg.dt,
        other_preds=other,
        min_dist=min_dist,
        num_headings=cfg.greedy_num_headings,
        slow_factor=cfg.greedy_slow_factor,
        stop_allowed=cfg.greedy_stop_allowed,
        alpha_goal=cfg.alpha_goal,
        beta_danger=cfg.beta_danger,
    )
    if v is not None:
        return v

    # A* fallback
    cell_size = cfg.cell_size
    start = world_to_cell(agent.pos, cell_size)
    goal = world_to_cell(agent.goal, cell_size)
    unsafe = build_unsafe_cells(other, cell_size)

    xmin = int(cfg.x_min // cell_size)
    xmax = int(cfg.x_max // cell_size)
    ymin = int(cfg.y_min // cell_size)
    ymax = int(cfg.y_max // cell_size)

    path = astar_path(start, goal, unsafe, ((xmin, ymin), (xmax, ymax)), cfg.astar_max_expansions)
    if not path or len(path) < 2:
        return (0.0, 0.0)

    target = cell_to_world(path[1], cell_size)
    d = sub(target, agent.pos)
    n = norm(d)
    if n == 0:
        return (0.0, 0.0)
    return mul((d[0]/n, d[1]/n), agent.max_speed)

def resolve_conflicts(agents: List[Agent], cfg) -> None:
    # default intent
    for a in agents:
        a.vel = (0.0, 0.0) if a.at_goal(cfg.goal_tolerance) else a.desired_velocity_to_goal()

    min_dist = (cfg.agent_radius * 2.0) + cfg.safety_margin
    preds = predict_all(agents, cfg.dt, cfg.horizon_steps)
    conflicts = find_conflicts(agents, preds, min_dist)

    by_id = {a.id: a for a in agents}
    for lo, hi in conflicts:
        # lo is higher priority; replan hi
        a = by_id.get(hi)
        if a is None or a.at_goal(cfg.goal_tolerance):
            continue
        preds_now = predict_all(agents, cfg.dt, cfg.horizon_steps)
        a.vel = choose_velocity(a, preds_now, cfg)

def tick(agents: List[Agent], cfg) -> bool:
    resolve_conflicts(agents, cfg)

    for a in agents:
        a.step(cfg.dt)
        a.pos = clamp(a.pos, cfg)

    # verify no actual collisions
    min_dist = (cfg.agent_radius * 2.0) + cfg.safety_margin
    for i in range(len(agents)):
        for j in range(i+1, len(agents)):
            if actual_collision(agents[i], agents[j], min_dist):
                return True
    return False
