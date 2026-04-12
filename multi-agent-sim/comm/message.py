from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class MsgType(str, Enum):
    PING = "PING"
    PONG = "PONG"
    HELLO = "HELLO"
    TASK = "TASK"
    STATUS = "STATUS"
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"

@dataclass(frozen=True)
class Message:
    msg_type: MsgType
    #the kind of message(see above)
    sender: str
    #who sent the message
    recipient: str  # can be "ALL" for broadcast (Day 2/5 improvements)
    #who should get the message
    tick: int
    #the time the msg was sent
    payload: dict[str, Any] | None = None
    #misc