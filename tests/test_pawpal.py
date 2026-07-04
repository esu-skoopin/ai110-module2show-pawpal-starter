import sys
import unittest
from datetime import date

# Repositories import streamlit; substitute a plain dict so tests run standalone.
class _SessionState(dict):
    pass

class _StreamlitStub:
    session_state = _SessionState()

sys.modules.setdefault("streamlit", _StreamlitStub())

import streamlit as st
from repositories.owner_repository import OwnerRepository
from repositories.pet_repository import PetRepository
from repositories.task_repository import TaskRepository


class TestTaskRepository(unittest.TestCase):
    def setUp(self):
        # Reset session state before each test to prevent cross-test pollution.
        st.session_state.clear()
        self.owner_repo = OwnerRepository()
        self.pet_repo = PetRepository()
        self.task_repo = TaskRepository()

        self.owner = self.owner_repo.create(first_name="Alex", last_name="Chen")
        self.pet = self.pet_repo.create(owner_id=self.owner.id, name="Mochi", animal_type="cat")
        self.today = date.today()

    def _tasks_for_pet(self) -> list:
        return [
            t for t in self.task_repo.get_by_owner_by_date(self.owner.id, self.today)
            if t.pet_id == self.pet.id
        ]

    def test_mark_complete_sets_completed_to_true(self):
        task = self.task_repo.create(
            pet_id=self.pet.id, name="Feed breakfast",
            note=None, duration=10,
            priority="essential", frequency="daily",
            scheduled_date=self.today,
        )
        self.assertFalse(task.completed)

        self.task_repo.mark_complete(task.id)

        self.assertTrue(task.completed)

    def test_adding_task_increases_pet_task_count(self):
        count_before = len(self._tasks_for_pet())

        self.task_repo.create(
            pet_id=self.pet.id, name="Morning walk",
            note=None, duration=30,
            priority="essential", frequency="daily",
            scheduled_date=self.today,
        )

        count_after = len(self._tasks_for_pet())
        self.assertEqual(count_after, count_before + 1)


if __name__ == "__main__":
    unittest.main()
