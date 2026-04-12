from dataclasses import dataclass
from typing import Tuple, Optional

Vec2 = Tuple[float, float]

@dataclass
class Task:
    id: int
    location: Vec2
    priority: int = 1
    assigned_to: Optional[int] = None
    completed: bool = False
