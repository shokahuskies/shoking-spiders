# integrated_demo.py
# Combines swarm_sim (tasking) with traj_avoid (safe motion).
# Requires both folders present.

# swarm_sim imports
from swarm_sim.config import SwarmConfig
from swarm_sim.world import World
from swarm_sim.allocation.auction import allocate_auction

# traj_avoid imports
from traj_avoid.config import Config as MotionConfig
from traj_avoid.agent import Agent as MotionAgent
from traj_avoid.sim import tick as motion_tick
from traj_avoid.viz import animate

def main():
    swarm_cfg = SwarmConfig()
    motion_cfg = MotionConfig()

    # Create a swarm world (high-level state)
    world = World.random_world(swarm_cfg, n_agents=8, seed=3)

    # Create motion agents that mirror swarm agents
    motion_agents = [
        MotionAgent(
            id=a.id,
            pos=a.pos,
            vel=(0.0, 0.0),
            goal=(a.pos[0], a.pos[1]),  # temporarily self
            radius=motion_cfg.agent_radius,
            max_speed=motion_cfg.max_speed,
        )
        for a in world.agents
    ]

    # Helper: sync swarm -> motion
    def sync_goals():
        # allocate tasks and write goals into swarm agents
        assignments = allocate_auction(world.agents, world.tasks)
        world.apply_assignments(assignments)

        # copy goals into motion agents (if None, keep current position)
        by_id = {a.id: a for a in world.agents}
        for ma in motion_agents:
            sa = by_id[ma.id]
            if sa.goal is not None:
                ma.goal = sa.goal
            else:
                ma.goal = ma.pos  # idle

    # Our animation tick: run motion every frame; run allocation every few ticks
    def integrated_tick(_agents, _cfg):
        # every X ticks, reassign tasks (swarm layer)
        if world.tick % swarm_cfg.decision_period_ticks == 0:
            sync_goals()

        # run collision-avoiding motion
        collision = motion_tick(motion_agents, motion_cfg)

        # update swarm positions from motion positions (so allocation uses real positions)
        by_id = {a.id: a for a in world.agents}
        for ma in motion_agents:
            by_id[ma.id].pos = ma.pos

        # let swarm world mark completions / drain battery
        world.step_high_level()

        return collision

    # start with initial assignment
    sync_goals()
    animate(motion_agents, tick_fn=integrated_tick, cfg=motion_cfg)

if __name__ == "__main__":
    main()
