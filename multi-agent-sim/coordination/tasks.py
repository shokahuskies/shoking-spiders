from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

Vec2 = Tuple[float, float]


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    DONE = "DONE"


@dataclass
class Task:
    task_id: str
    work_ticks: int
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    location: Optional[Vec2] = None
