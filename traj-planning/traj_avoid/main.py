from .config import Config
from .agent import Agent
from .sim import tick
from .viz import animate

def make_demo(cfg: Config):
    return [
        Agent(0, (2, 2), (0, 0), (18, 18), cfg.agent_radius, cfg.max_speed),
        Agent(1, (18, 2), (0, 0), (2, 18), cfg.agent_radius, cfg.max_speed),
        Agent(2, (2, 18), (0, 0), (18, 2), cfg.agent_radius, cfg.max_speed),
        Agent(3, (18, 18), (0, 0), (2, 2), cfg.agent_radius, cfg.max_speed),
        Agent(4, (10, 2), (0, 0), (10, 18), cfg.agent_radius, cfg.max_speed),
        Agent(5, (10, 18), (0, 0), (10, 2), cfg.agent_radius, cfg.max_speed),
    ]

def main():
    cfg = Config()
    agents = make_demo(cfg)
    animate(agents, tick_fn=tick, cfg=cfg)

if __name__ == "__main__":
    main()
