from dataclasses import dataclass
import math
from typing import Tuple

Vec2 = Tuple[float, float]

def add(a: Vec2, b: Vec2) -> Vec2: return (a[0] + b[0], a[1] + b[1])
def sub(a: Vec2, b: Vec2) -> Vec2: return (a[0] - b[0], a[1] - b[1])
def mul(a: Vec2, s: float) -> Vec2: return (a[0] * s, a[1] * s)
def norm(a: Vec2) -> float: return math.hypot(a[0], a[1])

def unit(a: Vec2) -> Vec2:
    n = norm(a)
    return (0.0, 0.0) if n == 0 else (a[0] / n, a[1] / n)

@dataclass
class Agent:
    id: int
    pos: Vec2
    vel: Vec2
    goal: Vec2
    radius: float
    max_speed: float

    def at_goal(self, tol: float) -> bool:
        return norm(sub(self.goal, self.pos)) <= tol

    def desired_velocity_to_goal(self) -> Vec2:
        return mul(unit(sub(self.goal, self.pos)), self.max_speed)

    def step(self, dt: float) -> None:
        self.pos = add(self.pos, mul(self.vel, dt))
