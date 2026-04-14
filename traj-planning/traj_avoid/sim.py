from typing import Dict, List, Tuple
from .agent import Agent, sub, norm, mul, add
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

def resolve_conflicts(agents: List[Agent], cfg) -> int:
    for a in agents:
        a.vel = (0.0, 0.0) if a.at_goal(cfg.goal_tolerance) else a.desired_velocity_to_goal()

    min_dist = (cfg.agent_radius * 2.0) + cfg.safety_margin
    preds = predict_all(agents, cfg.dt, cfg.horizon_steps)
    conflicts = find_conflicts(agents, preds, min_dist)

    # Collect every agent involved in any conflict; replan each only once.
    # Process in ascending ID order (lower id = higher priority) so later
    # agents plan around already-committed velocities.
    to_replan: set[int] = set()
    for lo, hi in conflicts:
        to_replan.add(lo)
        to_replan.add(hi)

    by_id = {a.id: a for a in agents}
    for agent_id in sorted(to_replan):
        a = by_id.get(agent_id)
        if a is None or a.at_goal(cfg.goal_tolerance):
            continue
        preds_now = predict_all(agents, cfg.dt, cfg.horizon_steps)
        a.vel = choose_velocity(a, preds_now, cfg)

    return len(conflicts)

def tick(agents: List[Agent], cfg) -> dict:
    # First resolve conflicts and get how many predicted conflicts existed
    predicted_conflicts = resolve_conflicts(agents, cfg)

    for a in agents:
        a.step(cfg.dt)
        a.pos = clamp(a.pos, cfg)

    min_dist = (cfg.agent_radius * 2.0) + cfg.safety_margin
    actual_collisions = 0
    collision_pairs = []

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            ai, aj = agents[i], agents[j]
            if actual_collision(ai, aj, min_dist):
                actual_collisions += 1
                collision_pairs.append((ai.id, aj.id))

                # Push overlapping agents apart so avoidance has a clean
                # starting state next tick — without this they deadlock forever
                d = sub(ai.pos, aj.pos)
                dist = norm(d)
                if dist > 0:
                    push = mul(d, (min_dist - dist) / dist * 0.5)
                else:
                    push = (min_dist * 0.5, 0.0)  # same-position fallback
                ai.pos = clamp(add(ai.pos, push), cfg)
                aj.pos = clamp(sub(aj.pos, push), cfg)

    done_agents = sum(1 for a in agents if a.at_goal(cfg.goal_tolerance))

    return {
        "predicted_conflicts": predicted_conflicts,
        "actual_collisions": actual_collisions,
        "collision_pairs": collision_pairs,
        "done_agents": done_agents,
    }