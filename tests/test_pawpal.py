import sys
import unittest
from datetime import date, time

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
from pawpal_system import Scheduler


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
            priority="Essential", recurrence="Daily",
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
            priority="Essential", recurrence="Daily",
            scheduled_date=self.today,
        )

        count_after = len(self._tasks_for_pet())
        self.assertEqual(count_after, count_before + 1)

    def test_mark_complete_recurring_creates_next_instance(self):
        task = self.task_repo.create(
            pet_id=self.pet.id, name="Weekly bath",
            note=None, duration=20,
            priority="Preferred", recurrence="Weekly",
            scheduled_date=self.today,
        )
        store_size_before = len(st.session_state["tasks"])

        self.task_repo.mark_complete(task.id)

        store_size_after = len(st.session_state["tasks"])
        self.assertEqual(store_size_after, store_size_before + 1)

        from datetime import timedelta
        expected_next = self.today + timedelta(weeks=1)
        new_tasks = [
            t for t in st.session_state["tasks"].values()
            if t.name == "Weekly bath" and t.scheduled_date == expected_next
        ]
        self.assertEqual(len(new_tasks), 1)
        self.assertFalse(new_tasks[0].completed)

    def test_mark_complete_non_recurring_creates_no_next_instance(self):
        task = self.task_repo.create(
            pet_id=self.pet.id, name="One-time vet visit",
            note=None, duration=60,
            priority="Essential", recurrence="None",
            scheduled_date=self.today,
        )
        store_size_before = len(st.session_state["tasks"])

        self.task_repo.mark_complete(task.id)

        store_size_after = len(st.session_state["tasks"])
        self.assertEqual(store_size_after, store_size_before)


class TestSchedulerSortAndFilter(unittest.TestCase):
    def setUp(self):
        st.session_state.clear()
        owner_repo = OwnerRepository()
        pet_repo = PetRepository()
        task_repo = TaskRepository()

        owner = owner_repo.create(first_name="Sam", last_name="Park")
        pet1 = pet_repo.create(owner_id=owner.id, name="Biscuit", animal_type="dog")
        pet2 = pet_repo.create(owner_id=owner.id, name="Whisker", animal_type="cat")
        today = date.today()

        task_a = task_repo.create(
            pet_id=pet1.id, name="Morning walk",
            note=None, duration=30, priority="Essential", recurrence="Daily",
            scheduled_date=today,
        )
        task_b = task_repo.create(
            pet_id=pet1.id, name="Evening walk",
            note=None, duration=20, priority="Preferred", recurrence="Daily",
            scheduled_date=today,
        )
        task_c = task_repo.create(
            pet_id=pet2.id, name="Brush fur",
            note=None, duration=10, priority="Low", recurrence="Weekly",
            scheduled_date=today,
        )
        task_b.completed = True

        self.pet1_id = pet1.id
        self.pet2_id = pet2.id

        # Build a hand-crafted results list similar to what generate_schedule() returns.
        self.results = [
            {"task": task_a, "scheduled": True,  "scheduled_time": time(9, 0),  "message": ""},
            {"task": task_b, "scheduled": True,  "scheduled_time": time(7, 30), "message": ""},
            {"task": task_c, "scheduled": False, "scheduled_time": None,        "message": "no window"},
        ]

        self.scheduler = Scheduler(task_repo=task_repo, availability_repo=None)

    # ── sort_by_scheduled_time ──────────────────────────────────────────────

    def test_sort_places_earlier_time_first(self):
        sorted_results = self.scheduler.sort_by_scheduled_time(self.results)
        scheduled = [r for r in sorted_results if r["scheduled"]]
        self.assertEqual(scheduled[0]["scheduled_time"], time(7, 30))
        self.assertEqual(scheduled[1]["scheduled_time"], time(9, 0))

    def test_sort_places_unscheduled_last(self):
        sorted_results = self.scheduler.sort_by_scheduled_time(self.results)
        self.assertFalse(sorted_results[-1]["scheduled"])

    def test_sort_empty_list_returns_empty(self):
        self.assertEqual(self.scheduler.sort_by_scheduled_time([]), [])

    # ── filter_tasks ────────────────────────────────────────────────────────

    def test_filter_by_completed_true(self):
        filtered = self.scheduler.filter_tasks(self.results, completed=True)
        self.assertTrue(all(r["task"].completed for r in filtered))
        self.assertEqual(len(filtered), 1)

    def test_filter_by_completed_false(self):
        filtered = self.scheduler.filter_tasks(self.results, completed=False)
        self.assertTrue(all(not r["task"].completed for r in filtered))
        self.assertEqual(len(filtered), 2)

    def test_filter_by_pet_id(self):
        filtered = self.scheduler.filter_tasks(self.results, pet_id=self.pet2_id)
        self.assertTrue(all(r["task"].pet_id == self.pet2_id for r in filtered))
        self.assertEqual(len(filtered), 1)

    def test_filter_combined_completed_and_pet(self):
        filtered = self.scheduler.filter_tasks(
            self.results, completed=True, pet_id=self.pet1_id
        )
        self.assertEqual(len(filtered), 1)
        self.assertTrue(filtered[0]["task"].completed)
        self.assertEqual(filtered[0]["task"].pet_id, self.pet1_id)

    def test_filter_no_args_returns_all(self):
        filtered = self.scheduler.filter_tasks(self.results)
        self.assertEqual(len(filtered), len(self.results))

    def test_filter_no_matches_returns_empty(self):
        filtered = self.scheduler.filter_tasks(self.results, pet_id=9999)
        self.assertEqual(filtered, [])


if __name__ == "__main__":
    unittest.main()
