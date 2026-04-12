from src.config import SimConfig
from src.sim.world import World

def run_demo(name: str, cfg: SimConfig) -> None:
    print(f"\n=== {name} ===")
    w = World.default(cfg)
    w.run()

if __name__ == "__main__":
    # Normal run: no crash
    cfg_ok = SimConfig(ticks=25, crash_agent=None, crash_tick=None)
    run_demo("DEMO 1: Normal operation", cfg_ok)

    # Failure run: crash A2 and show recovery
    cfg_fail = SimConfig(ticks=30, crash_agent="A2", crash_tick=8, timeout_ticks=5)
    run_demo("DEMO 2: Worker failure + task reassignment", cfg_fail)
