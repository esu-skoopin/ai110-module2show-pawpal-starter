from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Owner:
	id: Optional[int] = field(default=None, init=False)
	first_name: str
	last_name: str
