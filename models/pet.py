from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    id: Optional[int] = field(default=None, init=False)
    name: str
    owner_id: int
    animal_type: Optional[str] = None
    breed: Optional[str] = None
