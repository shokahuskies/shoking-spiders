from __future__ import annotations
from dataclasses import dataclass

from ..config import SimConfig
from comm.message import MsgType
from comm.network import Network
from ..agents.simple_agent import SimpleAgent
from coordination.coordinator import Coordinator
from coordination.tasks import Task, TaskStatus
from .clock import Clock
from .logger import Logger

@dataclass
class World:
    cfg: SimConfig
    clock: Clock
    net: Network
    agents: list[SimpleAgent]
    logger: Logger
    coordinator: Coordinator

    @classmethod
    def default(cls, cfg: SimConfig) -> "World":
        clock = Clock()
        net = Network(cfg)
        logger = Logger(enabled=True)

        agents = [SimpleAgent(f"A{i}", leader_id="A0", cfg=cfg) for i in range(1, 3)]
        net.register("A0")
        for a in agents:
            net.register(a.agent_id)

        # Day 2: leader is A0
        tasks = [Task(task_id=f"T{i}", work_ticks=2 + (i % 3)) for i in range(6)]
        coordinator = Coordinator(leader_id="A0", tasks=tasks)

        return cls(cfg=cfg, clock=clock, net=net, agents=agents, logger=logger, coordinator=coordinator)

    def run(self) -> None:
        self.logger.log(f"Starting sim for {self.cfg.ticks} ticks")

        workers = [a.agent_id for a in self.agents]

        for _ in range(self.cfg.ticks):
            t = self.clock.tick

            self.net.tick(t)

            # Leader receives STATUS and updates coordinator state
            for msg in self.net.recv_all("A0"):
                if msg.msg_type == MsgType.STATUS:
                    self.coordinator.handle_status(t, msg)
                elif msg.msg_type == MsgType.HEARTBEAT:
                    self.coordinator.handle_heartbeat(t, msg)

            # failure detection
            newly_failed = self.coordinator.detect_failures(t, self.cfg.timeout_ticks)
            for worker_id in newly_failed:
                self.logger.log(f"[t={t}] DETECTED FAILURE: {worker_id}")

            # Leader assigns tasks to idle workers
            self.coordinator.assign_tasks(t, self.net, workers)

            # Step all agents (including A0 as a worker-like agent for now)
            for a in self.agents:
                a.step(t, self.net)

            self.clock.advance()

        # Print summary
        done = sum(1 for task in self.coordinator.tasks if task.status == TaskStatus.DONE)
        self.logger.log(f"Sim done. Tasks completed: {done}/{len(self.coordinator.tasks)}")
