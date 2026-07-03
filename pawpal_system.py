from __future__ import annotations
from datetime import date, time
from typing import Optional

from models.availability import Availability
from models.task import Task
from repositories.task_repository import TaskRepository
from repositories.availability_repository import AvailabilityRepository


PRIORITY_ORDER = {"essential": 0, "preferred": 1, "low": 2}


class Scheduler:
    def __init__(self, task_repo: TaskRepository, availability_repo: AvailabilityRepository):
        self.task_repo = task_repo
        self.availability_repo = availability_repo

    def generate_schedule(self, owner_id: int, query_date: date) -> list[dict]:
        """
        Assigns a scheduled_time to each task for the given owner and date.

        Algorithm — two passes over each availability window:
          Pass 1 (anchor): tasks with a preferred_time that falls inside the
            window are placed at exactly that time, provided the slot is free.
            Within pass 1, tasks are ordered by priority then preferred_time so
            higher-priority preferences win conflicts.
          Pass 2 (fill): remaining unscheduled tasks are placed at the earliest
            free slot in each window (priority → duration ascending).

        Returns a list of result dicts (one per task), each containing:
          - task: the Task instance (scheduled_time updated if placed)
          - scheduled_time: time | None
          - scheduled: bool
          - reason: human-readable explanation
        """
        tasks = self.task_repo.get_by_owner_by_date(owner_id, query_date)
        windows = self.availability_repo.get_by_owner_by_day_of_week(
            owner_id, query_date.weekday()
        )
        windows = sorted(windows, key=lambda w: w.start_time or time(0, 0))

        sorted_tasks = sorted(
            tasks,
            key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.duration),
        )

        scheduled_ids: set[int] = set()
        results: list[dict] = []

        # occupied[window_index] = list of (start_min, end_min) intervals already claimed
        occupied: list[list[tuple[int, int]]] = [[] for _ in windows]

        # Pass 1: anchor tasks at their preferred_time
        for i, window in enumerate(windows):
            if window.start_time is None or window.end_time is None:
                continue
            win_start = self._time_to_minutes(window.start_time)
            win_end = self._time_to_minutes(window.end_time)

            anchors = [
                t for t in sorted_tasks
                if t.id not in scheduled_ids
                and t.preferred_time is not None
                and win_start <= self._time_to_minutes(t.preferred_time) < win_end
            ]
            anchors.sort(key=lambda t: (
                PRIORITY_ORDER.get(t.priority, 99),
                self._time_to_minutes(t.preferred_time),  # type: ignore[arg-type]
            ))

            for task in anchors:
                pt = self._time_to_minutes(task.preferred_time)  # type: ignore[arg-type]
                pt_end = pt + task.duration
                if pt_end <= win_end and self._slot_is_free(pt, pt_end, occupied[i]):
                    start = self._minutes_to_time(pt)
                    task.scheduled_time = start
                    if task.id is not None:
                        scheduled_ids.add(task.id)
                    occupied[i].append((pt, pt_end))
                    results.append({
                        "task": task,
                        "scheduled_time": start,
                        "scheduled": True,
                        "reason": self._build_reason(task, window, start, preferred_honored=True),
                    })

        # Pass 2: fill remaining gaps with unscheduled tasks
        for i, window in enumerate(windows):
            if window.start_time is None or window.end_time is None:
                continue
            win_start = self._time_to_minutes(window.start_time)
            win_end = self._time_to_minutes(window.end_time)

            for task in sorted_tasks:
                if task.id in scheduled_ids:
                    continue
                slot = self._find_earliest_slot(win_start, win_end, task.duration, occupied[i])
                if slot is not None:
                    start = self._minutes_to_time(slot)
                    task.scheduled_time = start
                    if task.id is not None:
                        scheduled_ids.add(task.id)
                    occupied[i].append((slot, slot + task.duration))
                    preferred_honored = (
                        task.preferred_time is not None
                        and self._time_to_minutes(task.preferred_time) == slot
                    )
                    results.append({
                        "task": task,
                        "scheduled_time": start,
                        "scheduled": True,
                        "reason": self._build_reason(task, window, start,
                                                     preferred_honored=preferred_honored),
                    })

        for task in sorted_tasks:
            if task.id not in scheduled_ids:
                results.append({
                    "task": task,
                    "scheduled_time": None,
                    "scheduled": False,
                    "reason": (
                        f"'{task.name}' ({task.duration} min) could not fit into "
                        "any available window for this day."
                    ),
                })

        return results

    # ------------------------------------------------------------------ helpers

    def _slot_is_free(self, start: int, end: int,
                      occupied: list[tuple[int, int]]) -> bool:
        return not any(s < end and start < e for s, e in occupied)

    def _find_earliest_slot(self, win_start: int, win_end: int, duration: int,
                            occupied: list[tuple[int, int]]) -> Optional[int]:
        # Candidates are the window start and the end of every occupied interval.
        candidates = sorted({win_start} | {e for _, e in occupied})
        for candidate in candidates:
            if candidate < win_start:
                continue
            if candidate + duration <= win_end and self._slot_is_free(candidate, candidate + duration, occupied):
                return candidate
        return None

    def _build_reason(self, task: Task, window: Availability,
                      start: time, preferred_honored: bool = False) -> str:
        window_label = self._format_window(window)
        parts = [f"Scheduled at {start.strftime('%H:%M')} within the {window_label} window."]
        if task.preferred_time is not None:
            if preferred_honored:
                parts.append(f"Preferred time {task.preferred_time.strftime('%H:%M')} honored.")
            else:
                parts.append(
                    f"Preferred time {task.preferred_time.strftime('%H:%M')} unavailable; "
                    "placed at next free slot."
                )
        parts += [
            f"Priority: {task.priority.capitalize()}.",
            f"Duration: {task.duration} min.",
        ]
        if task.note:
            parts.append(f"Note: {task.note}")
        return " ".join(parts)

    def _format_window(self, window: Availability) -> str:
        if window.start_time is None or window.end_time is None:
            return "unknown window"
        return (
            f"{window.start_time.strftime('%H:%M')}–"
            f"{window.end_time.strftime('%H:%M')}"
        )

    def _time_to_minutes(self, t: time) -> int:
        return t.hour * 60 + t.minute

    def _minutes_to_time(self, minutes: int) -> time:
        return time(minutes // 60, minutes % 60)
