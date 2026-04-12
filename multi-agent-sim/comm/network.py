from __future__ import annotations
import random
from dataclasses import dataclass

from src.config import SimConfig
from .message import Message

@dataclass
class Network:
    """
    Day 1: immediate delivery
    Day 5: delayed delivery, probabilistic drops, buffering
    """
    cfg: SimConfig

    def __post_init__(self) -> None:
        self.rng = random.Random(self.cfg.seed)
        self.inboxes: dict[str, list[Message]] = {}
        self.scheduled: list[tuple[int, Message]] = []
        self.stats: dict[str, int] = {
            "sent": 0,
            "dropped": 0,
            "delivered": 0,
            "overflow_dropped": 0,
            "scheduled": 0,
        }

    def register(self, agent_id: str) -> None:
        """registers an inbox for a new agent

        setdefault :: if the key exists in the dict, return value.
        if not, insert key (default and return default)"""
        self.inboxes.setdefault(agent_id, [])

    def send(self, msg: Message) -> None:
        """send a msg to the recipient's inbox
        through using a message from message.py"""
        self.stats["sent"] += 1

        # DROP?
        if self.cfg.drop_prob > 0.0 and self.rng.random() < self.cfg.drop_prob:
            self.stats["dropped"] += 1
            return

        # DELAY
        delay = 0
        if self.cfg.max_delay > 0:
            lo = max(0, self.cfg.min_delay)
            hi = max(lo, self.cfg.max_delay)
            delay = self.rng.randint(lo, hi)

        if delay == 0:
            self._deliver(msg)
        else:
            deliver_t = msg.tick + delay
            self.scheduled.append((deliver_t, msg))
            self.stats["scheduled"] += 1

    def broadcast(self, msg: Message) -> None:
        """broadcast a copy of a message to all registered agents (except for the sender)

        note that this also creates a new msg OBJECT."""
        for aid in list(self.inboxes.keys()):
            if aid == msg.sender:
                continue
            self.send(
                Message(
                    msg_type=msg.msg_type,
                    sender=msg.sender,
                    recipient=aid,
                    tick=msg.tick,
                    payload=msg.payload,
                )
            )

    def tick(self, current_tick: int) -> None:
        """deliver any scheduled messages whose delivery time has arrived"""
        due = [msg for deliver_t, msg in self.scheduled if deliver_t <= current_tick]
        self.scheduled = [(deliver_t, msg) for deliver_t, msg in self.scheduled if deliver_t > current_tick]
        for msg in due:
            self._deliver(msg)

    def recv_all(self, agent_id: str) -> list[Message]:
        """this returns all of the msg for an agent and clears their inbox

        drain op at this level"""
        msgs = self.inboxes.get(agent_id, [])
        self.inboxes[agent_id] = []
        return msgs

    def _deliver(self, msg: Message) -> None:
        inbox = self.inboxes.setdefault(msg.recipient, [])

        cap = max(0, int(self.cfg.inbox_capacity))
        if cap == 0:
            self.stats["overflow_dropped"] += 1
            return

        if len(inbox) >= cap:
            if self.cfg.overflow_policy == "drop_old":
                inbox.pop(0)
                inbox.append(msg)
                self.stats["delivered"] += 1
            else:
                self.stats["overflow_dropped"] += 1
            return

        inbox.append(msg)
        self.stats["delivered"] += 1
