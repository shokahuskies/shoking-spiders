from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from .message import Message

@dataclass
class Mailbox:
    """since this is a situation where time matters,
    we use encapsulation"""
    _q: deque[Message]

    def __init__(self) -> None:
        self._q = deque()

    def push(self, msg: Message) -> None:
        """we take a msg and append it to the list ._q"""
        self._q.append(msg)

    def pop(self) -> Message | None:
        """uses FIFO --> ensures that this returns the msg that
        needs to be processed while removing it from the list
        (since it should already be processed)

        we want to use this when we have independent messages,
        and when we take the order of the msg matters more than task completeness.
        This also imitates limited design (processing msg one by one)"""
        if not self._q:
            return None
        return self._q.popleft()

    def drain(self, limit: int | None = None) -> list[Message]:
        """we take a snapshot of all the messages we have received so far and we process it as a batch.
        aka "tell me everything that happened since the last time i checked." """
        out: list[Message] = []
        n = len(self._q) if limit is None else min(limit, len(self._q))
        for _ in range(n):
            out.append(self._q.popleft())
        return out

    def __len__(self) -> int:
        return len(self._q)
