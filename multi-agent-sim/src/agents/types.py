from enum import Enum

class AgentRole(str, Enum):
    LEADER = "LEADER"
    WORKER = "WORKER"

class AgentMode(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
