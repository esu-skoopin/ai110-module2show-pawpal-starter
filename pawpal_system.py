from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

@dataclass
class Owner:
    first_name: str
    last_name: str
    id: Optional[int] = field(default=None, init=False)

    def create_owner(self):
        pass

    def get_owner(self):
        pass

    def edit_owner(self):
        pass


@dataclass
class Pet:
    name: str
    owner_id: int
    animal_type: Optional[str] = None
    breed: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

    def create_pet(self):
        pass

    def get_pets_by_owner(self):
        pass

    def get_pet(self):
        pass

    def edit_pet(self):
        pass


@dataclass
class Task:
    pet_id: int
    name: str
    duration: int
    priority: str
    frequency: str
    scheduled_date: date
    scheduled_time: time
    completed: bool = False
    note: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

    def create_task(self):
        pass

    def get_task(self):
        pass

    def get_tasks_by_owner_by_date(self):
        pass

    def get_tasks_by_owner_by_date_range(self):
        pass

    def edit_task(self):
        pass


@dataclass
class OwnerAvailability:
    owner_id: int
    day_of_week: int
    start_time: time
    end_time: time
    id: Optional[int] = field(default=None, init=False)

    def get_owner_availability_by_day_of_week(self):
        pass
