from __future__ import annotations
from datetime import date, time, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional
import streamlit as st
from models.task import Task
from repositories.pet_repository import PetRepository


class TaskRepository:
    def __init__(self):
        st.session_state.setdefault("tasks", {})
        st.session_state.setdefault("next_task_id", 1)

    @property
    def _store(self) -> dict[int, Task]:
        return st.session_state["tasks"]

    @property
    def _next_id(self) -> int:
        return st.session_state["next_task_id"]

    @_next_id.setter
    def _next_id(self, value: int) -> None:
        st.session_state["next_task_id"] = value

    def create(self, pet_id: int, name: str, note: Optional[str], duration: int,
               priority: str, recurrence: str, scheduled_date: date,
               preferred_time: Optional[time] = None) -> Task:
        task = Task(
            id=self._next_id,
            pet_id=pet_id,
            name=name,
            note=note,
            duration=duration,
            priority=priority,
            recurrence=recurrence,
            scheduled_date=scheduled_date,
            preferred_time=preferred_time
        )
        self._next_id += 1
        self._store[task.id] = task
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self._store.get(task_id)

    def get_by_owner_by_date(self, owner_id: int, query_date: date) -> list[Task]:
        pet_ids = {p.id for p in PetRepository().get_by_owner(owner_id)}
        return [t for t in self._store.values()
                if t.pet_id in pet_ids and t.scheduled_date == query_date]

    def get_by_owner_by_date_range(self, owner_id: int,
                                   start_date: date, end_date: date) -> list[Task]:
        pet_ids = {p.id for p in PetRepository().get_by_owner(owner_id)}
        return [t for t in self._store.values()
                if t.pet_id in pet_ids
                and t.scheduled_date is not None
                and start_date <= t.scheduled_date <= end_date]

    def update(self, task_id: int, name: str, note: Optional[str], duration: int,
               priority: str, recurrence: str, scheduled_date: date,
               completed: bool, preferred_time: Optional[time] = None) -> Optional[Task]:
        task = self.get(task_id)
        if task is None:
            return None
        task.name = name
        task.note = note
        task.duration = duration
        task.priority = priority
        task.recurrence = recurrence
        task.scheduled_date = scheduled_date
        task.completed = completed
        task.preferred_time = preferred_time
        return task
    
    def mark_complete(self, task_id: int) -> Optional[Task]:
        """Mark the task as completed and schedule the next occurrence if it recurs."""
        task = self.get(task_id)
        if task is None:
            return None
        task.completed = True
        next_date = self._next_occurrence(task)
        if next_date is not None:
            self.create(
                pet_id=task.pet_id,
                name=task.name,
                note=task.note,
                duration=task.duration,
                priority=task.priority,
                recurrence=task.recurrence,
                scheduled_date=next_date,
                preferred_time=task.preferred_time,
            )
        return task

    _RECURRENCE_DELTAS: dict[str, timedelta | relativedelta] = {
        "Daily":   timedelta(days=1),
        "Weekly":  timedelta(weeks=1),
        "Monthly": relativedelta(months=1),
        "Yearly":  relativedelta(years=1),
    }

    def _next_occurrence(self, task: Task) -> Optional[date]:
        """Return the next scheduled_date for a recurring task, or None if non-recurring."""
        delta = self._RECURRENCE_DELTAS.get(task.recurrence)
        if delta is None or task.scheduled_date is None:
            return None
        next_dt = task.scheduled_date + delta
        return next_dt if isinstance(next_dt, date) else next_dt.date()

    def delete(self, task_id: int) -> bool:
        return self._store.pop(task_id, None) is not None
