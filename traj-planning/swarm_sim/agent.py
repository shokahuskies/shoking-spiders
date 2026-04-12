from dataclasses import dataclass
from typing import Tuple, Optional

Vec2 = Tuple[float, float]

@dataclass
class SwarmAgent:
    """
    High-level agent for allocation:
    - Stores current position, current goal, and battery.
    - Does NOT do collision avoidance here.
    """
    id: int
    pos: Vec2
    battery: float
    goal: Optional[Vec2] = None
    current_task_id: Optional[int] = None
