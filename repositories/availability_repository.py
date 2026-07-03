from __future__ import annotations
from datetime import time
from typing import Optional
import streamlit as st
from models.availability import Availability


class AvailabilityRepository:
    def __init__(self):
        st.session_state.setdefault("availabilities", {})
        st.session_state.setdefault("next_availability_id", 1)

    @property
    def _store(self) -> dict[int, Availability]:
        return st.session_state["availabilities"]

    @property
    def _next_id(self) -> int:
        return st.session_state["next_availability_id"]

    @_next_id.setter
    def _next_id(self, value: int) -> None:
        st.session_state["next_availability_id"] = value

    def create(self, owner_id: int, day_of_week: int,
               start_time: time, end_time: time) -> Availability:
        avail = Availability(owner_id=owner_id, day_of_week=day_of_week,
                             start_time=start_time, end_time=end_time)
        avail.id = self._next_id
        self._next_id += 1
        self._store[avail.id] = avail
        return avail

    def get(self, availability_id: int) -> Optional[Availability]:
        return self._store.get(availability_id)

    def get_by_owner(self, owner_id: int) -> list[Availability]:
        return [a for a in self._store.values() if a.owner_id == owner_id]

    def get_by_owner_by_day_of_week(self, owner_id: int, day_of_week: int) -> list[Availability]:
        return [a for a in self._store.values()
                if a.owner_id == owner_id and a.day_of_week == day_of_week]

    def update(self, availability_id: int, day_of_week: int,
               start_time: time, end_time: time) -> Optional[Availability]:
        avail = self.get(availability_id)
        if avail is None:
            return None
        avail.day_of_week = day_of_week
        avail.start_time = start_time
        avail.end_time = end_time
        return avail

    def delete(self, availability_id: int) -> bool:
        return self._store.pop(availability_id, None) is not None
