from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional


@dataclass
class Task:
    id: int
    pet_id: int
    name: str
    duration: int
    priority: str
    recurrence: str
    scheduled_date: date
    scheduled_time: Optional[time] = None
    preferred_time: Optional[time] = None
    note: Optional[str] = None
    completed: bool = False
