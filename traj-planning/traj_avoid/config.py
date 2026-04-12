from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    dt: float = 0.2
    max_ticks: int = 600
    horizon_steps: int = 12

    agent_radius: float = 0.4
    safety_margin: float = 0.2
    max_speed: float = 1.0

    x_min: float = 0.0
    x_max: float = 20.0
    y_min: float = 0.0
    y_max: float = 20.0

    greedy_num_headings: int = 16
    greedy_slow_factor: float = 0.6
    greedy_stop_allowed: bool = True
    alpha_goal: float = 1.0
    beta_danger: float = 8.0

    cell_size: float = 0.5
    astar_max_expansions: int = 40_000

    goal_tolerance: float = 0.5
