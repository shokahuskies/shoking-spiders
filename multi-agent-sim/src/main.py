from .config import SimConfig
from .sim.world import World

def main() -> None:
    cfg = SimConfig(ticks=10)
    w = World.default(cfg)
    w.run()

if __name__ == "__main__":
    main()
