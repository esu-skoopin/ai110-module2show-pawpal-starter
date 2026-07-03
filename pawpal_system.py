from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional


@dataclass
class Owner:
	id: Optional[int] = field(default=None, init=False)
	first_name: str
	last_name: str

	def create_owner(self, first_name: str, last_name: str):
		pass

	def get_owner(self, id: int):
		pass

	def edit_owner(self, id: int, first_name: str, last_name: str):
		pass

	def delete_owner(self, id: int):
		pass


@dataclass
class Pet:
	id: Optional[int] = field(default=None, init=False)
	name: str
	owner_id: int
	animal_type: Optional[str] = None
	breed: Optional[str] = None

	def create_pet(self, owner_id: int, name: str, animal_type: Optional[str], breed: Optional[str]):
		pass

	def get_pets_by_owner(self, owner_id: int):
		pass

	def get_pet(self, id: int):
		pass

	def edit_pet(self, id: int, name: str, animal_type: Optional[str], breed: Optional[str]):
		pass

	def delete_pet(self, id: int):
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

	def create_task(self, pet_id: int, name: str, note: Optional[str], duration: int,
					priority: str, frequency: str, scheduled_date: date):
		pass

	def get_task(self, id: int):
		pass

	def get_tasks_by_owner_by_date(self, owner_id: int, query_date: date):
		pass

	def get_tasks_by_owner_by_date_range(self, owner_id: int, start_date: date, end_date: date):
		pass

	def edit_task(self, id: int, name: str, note: Optional[str], duration: int,
				  priority: str, frequency: str, scheduled_date: date, completed: bool):
		pass

	def delete_task(self, id: int):
		pass


@dataclass
class OwnerAvailability:
	id: Optional[int] = field(default=None, init=False)
	owner_id: int
	day_of_week: int
	start_time: time
	end_time: time

	def create_availability(self, owner_id: int, day_of_week: int, start_time: time, end_time: time):
		pass

	def get_availabilities_by_owner(self, owner_id: int):
		pass

	def get_availabilities_by_owner_by_day_of_week(self, owner_id: int, day_of_week: int):
		pass

	def get_availability(self, id: int):
		pass

	def edit_availability(self, id: int, day_of_week: int, start_time: time, end_time: time):
		pass

	def delete_availability(self, id: int):
		pass


class Scheduler:
	def generate_schedule(self, owner_id: int, query_date: date):
		pass
