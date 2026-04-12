from dataclasses import dataclass

@dataclass
class Clock:
    tick: int = 0

    def advance(self) -> int:
        self.tick += 1
        return self.tick
