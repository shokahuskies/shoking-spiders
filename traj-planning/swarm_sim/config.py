from dataclasses import dataclass

@dataclass(frozen=True)
class SwarmConfig:
    world_w: float = 20.0
    world_h: float = 20.0

    # Task generation
    initial_tasks: int = 12

    # Battery/energy model (simple)
    battery_max: float = 100.0
    battery_drain_per_unit: float = 0.2  # per unit distance moved (used in metrics/sim)

    # Timing
    decision_period_ticks: int = 15  # how often to re-allocate tasks
