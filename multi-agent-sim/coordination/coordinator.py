from __future__ import annotations
from dataclasses import dataclass

from comm.message import Message, MsgType
from comm.network import Network
from .tasks import Task, TaskStatus

@dataclass
class Coordinator:
    leader_id: str
    tasks: list[Task]
    busy: dict[str, str]  # agent_id -> task_id

    def __init__(self, leader_id: str, tasks: list[Task]) -> None:
        self.leader_id = leader_id
        self.tasks = tasks
        self.busy: dict[str, str] = {}
        self.last_seen: dict[str, int] = {}
        self.failed: set[str] = set()

    def handle_heartbeat(self, tick: int, msg: Message) -> None:
        if msg.sender in self.failed:
            return
        self.last_seen[msg.sender] = tick

    def detect_failures(self, tick: int, timeout_ticks: int) -> list[str]:
        newly_failed: list[str] = []
        for wid, last in list(self.last_seen.items()):
            if wid in self.failed:
                continue
            if tick - last >= timeout_ticks:
                self.failed.add(wid)
                newly_failed.append(wid)

                # If this worker was busy, requeue its task
                task_id = self.busy.pop(wid, None)
                if task_id is not None:
                    self._requeue_task(task_id)

        return newly_failed

    def _requeue_task(self, task_id: str) -> None:
        for t in self.tasks:
            if t.task_id == task_id and t.status != TaskStatus.DONE:
                t.status = TaskStatus.PENDING
                t.assigned_to = None
                return

    def handle_status(self, _tick: int, msg: Message) -> None:
        """
        Handles worker STATUS messages.
        Expected payload:
        {"kind": "ACK"|"DONE", "task_id": "..."}
        """
        if msg.payload is None:
            return
        kind = msg.payload.get("kind")
        task_id = msg.payload.get("task_id")
        if not kind or not task_id:
            return

        if kind == "ACK":
            # worker accepted the task; leader already considers them busy
            return

        if kind == "DONE":
            # mark task done + free worker
            for t in self.tasks:
                if t.task_id == task_id:
                    t.status = TaskStatus.DONE
                    break
            self.busy.pop(msg.sender, None)

    def assign_tasks(self, tick: int, net: Network, workers: list[str]) -> None:
        """
        Assign tasks to any idle worker, one task at a time.
        """
        for worker_id in workers:
            if worker_id in self.busy:
                continue  # already has a task

            if worker_id in self.failed:
                continue

            task = self._next_pending()
            if task is None:
                return  # no more tasks

            task.status = TaskStatus.ASSIGNED
            task.assigned_to = worker_id
            self.busy[worker_id] = task.task_id

            net.send(
                Message(
                    msg_type=MsgType.TASK,
                    sender=self.leader_id,
                    recipient=worker_id,
                    tick=tick,
                    payload={"task_id": task.task_id, "work_ticks": task.work_ticks},
                )
            )

    def assign_direct(self, worker_id: str) -> Task | None:
        """Assign the next pending task to worker_id without a Network.
        Returns the Task if assigned, None if worker is busy/failed or no tasks remain."""
        if worker_id in self.busy or worker_id in self.failed:
            return None
        task = self._next_pending()
        if task is None:
            return None
        task.status = TaskStatus.ASSIGNED
        task.assigned_to = worker_id
        self.busy[worker_id] = task.task_id
        return task

    def complete_task(self, worker_id: str) -> Task | None:
        """Mark the task currently assigned to worker_id as DONE and free the worker.
        Returns the completed Task, or None if the worker had no assigned task."""
        task_id = self.busy.pop(worker_id, None)
        if task_id is None:
            return None
        for t in self.tasks:
            if t.task_id == task_id:
                t.status = TaskStatus.DONE
                t.assigned_to = None
                return t
        return None

    def _next_pending(self) -> Task | None:
        for t in self.tasks:
            if t.status == TaskStatus.PENDING:
                return t
        return None
