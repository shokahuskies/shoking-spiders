from dataclasses import dataclass

@dataclass
class SimConfig:
    seed: int = 0
    ticks: int = 30

    heartbeat_every: int = 2      # worker sends heartbeat every N ticks
    timeout_ticks: int = 5        # if leader hasn't heard in this many ticks -> failed

    crash_agent: str | None = "A2"  # for demo: crash A2
    crash_tick: int | None = 8      # when it crashes

    drop_prob: float = 0.0
    min_delay: int = 0
    max_delay: int = 0
    inbox_capacity: int = 50
    overflow_policy: str = "drop_new"