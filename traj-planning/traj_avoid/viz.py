from typing import List
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from .agent import Agent

def animate(agents: List[Agent], tick_fn, cfg) -> None:
    fig, ax = plt.subplots()
    ax.set_xlim(cfg.x_min, cfg.x_max)
    ax.set_ylim(cfg.y_min, cfg.y_max)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title("traj_avoid — Trajectory + Collision Avoidance")

    agent_scatter = ax.scatter([], [])
    goal_scatter = ax.scatter([], [], marker='x')
    status = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top")

    def init():
        agent_scatter.set_offsets(np.empty((0, 2)))
        goal_scatter.set_offsets(np.empty((0, 2)))
        status.set_text("")
        return agent_scatter, goal_scatter, status

    t = {"k": 0}
    stats = {"predicted_conflicts": 0, "actual_collisions": 0}
    history = []

    def update(_):
        result = tick_fn(agents, cfg)
        t["k"] += 1

        stats["predicted_conflicts"] += result["predicted_conflicts"]
        stats["actual_collisions"] += result["actual_collisions"]

        agent_scatter.set_offsets([(a.pos[0], a.pos[1]) for a in agents])
        goal_scatter.set_offsets([(a.goal[0], a.goal[1]) for a in agents])

        status.set_text(
            f"tick={t['k']} "
            f"done={result['done_agents']}/{len(agents)} "
            f"| predicted_total={stats['predicted_conflicts']} "
            f"| actual_total={stats['actual_collisions']}"
        )

        return agent_scatter, goal_scatter, status

    ani = FuncAnimation(fig, update, init_func=init, frames=cfg.max_ticks, interval=30, blit=True)
    plt.show()