from __future__ import annotations
from dataclasses import dataclass

from ..config import SimConfig
from .base import AgentState
from .types import AgentMode, AgentRole
from comm.message import Message, MsgType
from comm.network import Network

@dataclass
class SimpleAgent:
    agent_id: str
    leader_id: str
    state: AgentState
    cfg: SimConfig

    def __init__(self, agent_id: str, leader_id: str, cfg: SimConfig) -> None:
        self.agent_id = agent_id
        self.leader_id = leader_id
        self.state = AgentState(role=AgentRole.WORKER)
        self.cfg = cfg

    def step(self, tick: int, net: Network) -> None:

        if (
            self.cfg.crash_agent == self.agent_id
            and self.cfg.crash_tick is not None
            and tick >= self.cfg.crash_tick
        ):
            self.state.alive = False

        if not self.state.alive:
            return

        if self.cfg.heartbeat_every > 0 and tick % self.cfg.heartbeat_every == 0:
            net.send(
                Message(
                    msg_type=MsgType.HEARTBEAT,
                    sender=self.agent_id,
                    recipient=self.leader_id,
                    tick=tick,
                    payload=None,
                )
            )

        if self.state.mode == AgentMode.BUSY and self.state.busy_until_tick is not None:
            if tick >= self.state.busy_until_tick:
                net.send(
                    Message(
                        msg_type=MsgType.STATUS,
                        sender=self.agent_id,
                        recipient=self.leader_id,
                        tick=tick,
                        payload={"kind": "DONE", "task_id": self.state.current_task_id},
                    )
                )
                self.state.mode = AgentMode.IDLE
                self.state.current_task_id = None
                self.state.busy_until_tick = None

        # process inbound
        for msg in net.recv_all(self.agent_id):
            if msg.msg_type == MsgType.PING:
                net.send(
                    Message(
                        msg_type=MsgType.PONG,
                        sender=self.agent_id,
                        recipient=msg.sender,
                        tick=tick,
                        payload={"reply_to": "PING"},
                    )
                )

            if msg.msg_type == MsgType.TASK and msg.payload is not None:
                task_id = msg.payload.get("task_id")
                work_ticks = int(msg.payload.get("work_ticks", 3))

                self.state.mode = AgentMode.BUSY
                self.state.current_task_id = task_id
                self.state.busy_until_tick = tick + work_ticks

                net.send(
                    Message(
                        msg_type=MsgType.STATUS,
                        sender=self.agent_id,
                        recipient=msg.sender,
                        tick=tick,
                        payload={"kind": "ACK", "task_id": task_id},
                    )
                )

        # send a hello at tick 0
        if tick == 0:
            net.broadcast(
                Message(
                    msg_type=MsgType.HELLO,
                    sender=self.agent_id,
                    recipient="ALL",
                    tick=tick,
                    payload={"hi": True},
                )
            )
