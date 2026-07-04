from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Owner:
    id: int
    first_name: str
    last_name: str
