from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

@dataclass
class Owner:
	id: Optional[int] = field(default=None, init=False)
	first_name: str
	last_name: str

	def create_owner(self):
		pass

	def get_owner(self):
		pass

	def edit_owner(self):
		pass

	def delete_owner(self):
		pass

@dataclass
class Pet:
	id: Optional[int] = field(default=None, init=False)
	name: str
	owner_id: int
	animal_type: Optional[str] = None
	breed: Optional[str] = None

	def create_pet(self):
		pass

	def get_pets_by_owner(self):
		pass

	def get_pet(self):
		pass

	def edit_pet(self):
		pass

	def delete_pet(self):
		pass

@dataclass
class Task:
	id: Optional[int] = field(default=None, init=False)
	pet_id: int
	name: str
	duration: int
	priority: str
	frequency: str
	scheduled_date: date
	scheduled_time: Optional[time] = None
	note: Optional[str] = None
	completed: bool = False

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

	def delete_task(self):
		pass

@dataclass
class OwnerAvailability:
	id: Optional[int] = field(default=None, init=False)
	owner_id: int
	day_of_week: int
	start_time: time
	end_time: time
	
	def create_availability(self):
		pass

	def get_availabilities_by_owner(self):
		pass

	def get_availabilities_by_owner_by_day_of_week(self):
		pass

	def get_availability(self):
		pass

	def edit_availability(self):
		pass

	def delete_availability(self):
		pass
