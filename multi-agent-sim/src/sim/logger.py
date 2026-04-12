from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Logger:
    enabled: bool = True

    def log(self, s: str) -> None:
        if self.enabled:
            print(s)
