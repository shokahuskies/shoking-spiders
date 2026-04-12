from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

from comm.message import Message
from comm.network import Network
from .types import AgentRole, AgentMode

class Agent(Protocol):
    agent_id: str
    def step(self, tick: int, net: Network) -> None: ...

@dataclass
class AgentState:
    # Day 2/3: expand with role, known peers, task state, etc.
    alive: bool = True
    role: AgentRole = AgentRole.WORKER
    mode: AgentMode = AgentMode.IDLE

    current_task_id: str | None = None
    busy_until_tick: int | None = None
