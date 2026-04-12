from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    DONE = "DONE"


@dataclass
class Task:
    task_id: str
    work_ticks: int
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: str | None = None
