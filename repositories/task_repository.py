from __future__ import annotations
from datetime import date, time
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
               priority: str, frequency: str, scheduled_date: date,
               preferred_time: Optional[time] = None) -> Task:
        task = Task(
            id=self._next_id,
            pet_id=pet_id,
            name=name,
            note=note,
            duration=duration,
            priority=priority,
            frequency=frequency,
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
               priority: str, frequency: str, scheduled_date: date,
               completed: bool, preferred_time: Optional[time] = None) -> Optional[Task]:
        task = self.get(task_id)
        if task is None:
            return None
        task.name = name
        task.note = note
        task.duration = duration
        task.priority = priority
        task.frequency = frequency
        task.scheduled_date = scheduled_date
        task.completed = completed
        task.preferred_time = preferred_time
        return task
    
    def mark_complete(self, task_id: int) -> Optional[Task]:
        task = self.get(task_id)
        if task is None:
            return None
        task.completed = True
        return task

    def delete(self, task_id: int) -> bool:
        return self._store.pop(task_id, None) is not None
