from __future__ import annotations
from dataclasses import dataclass, field
from datetime import time
from typing import Optional


@dataclass
class Availability:
    id: Optional[int] = field(default=None, init=False)
    owner_id: int
    day_of_week: int
    start_time: time
    end_time: time
