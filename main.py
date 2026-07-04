import sys
from datetime import date, time

# Repositories import streamlit for session_state persistence.
# Outside of a Streamlit app, we substitute a plain dict so the script runs standalone.
class _SessionState(dict):
    pass

class _StreamlitStub:
    session_state = _SessionState()

sys.modules.setdefault("streamlit", _StreamlitStub())

from repositories.owner_repository import OwnerRepository
from repositories.pet_repository import PetRepository
from repositories.task_repository import TaskRepository
from repositories.availability_repository import AvailabilityRepository
from pawpal_system import Scheduler


def print_results(results: list[dict], pet_repo: PetRepository, title: str):
    print(f"\n{title}\n")
    if not results:
        print("(no tasks)")
        return
    print(f"{'TIME':<8} {'TASK':<18} {'PET':<8} {'COMPLETED'}")
    print(f"{'-' * 48}")
    for entry in results:
        task = entry["task"]
        pet = pet_repo.get(task.pet_id)
        pet_name = pet.name if pet else "?"
        t = entry["scheduled_time"].strftime("%H:%M") if entry["scheduled_time"] else "—"
        done = "Yes" if task.completed else "No"
        print(f"{t:<8} {task.name:<18} {pet_name:<8} {done}")


def main():
    owner_repo = OwnerRepository()
    pet_repo = PetRepository()
    task_repo = TaskRepository()
    avail_repo = AvailabilityRepository()

    # ── Owner ──────────────────────────────────────────────────────────────────
    owner = owner_repo.create(first_name="Alex", last_name="Chen")

    # ── Pets ───────────────────────────────────────────────────────────────────
    mochi = pet_repo.create(owner_id=owner.id, name="Mochi",
                            animal_type="cat", breed="Siamese")
    bruno = pet_repo.create(owner_id=owner.id, name="Bruno",
                            animal_type="dog", breed="Labrador")

    # ── Availability ───────────────────────────────────────────────────────────
    today = date.today()
    day = today.weekday()  # 0 = Monday … 6 = Sunday

    avail_repo.create(owner_id=owner.id, day_of_week=day,
                      start_time=time(8, 0), end_time=time(12, 0))
    avail_repo.create(owner_id=owner.id, day_of_week=day,
                      start_time=time(14, 0), end_time=time(18, 0))

    # ── Tasks ──────────────────────────────────────────────────────────────────
    morning_walk = task_repo.create(
        pet_id=bruno.id, name="Morning walk",
        note=None, duration=30,
        priority="Essential", recurrence="Daily",
        scheduled_date=today, preferred_time=time(8, 0),
    )
    task_repo.create(
        pet_id=mochi.id, name="Feed breakfast",
        note="Feed 1/4 cup kibble", duration=10,
        priority="Essential", recurrence="Daily",
        scheduled_date=today, preferred_time=time(8, 30),
    )
    clip_nails = task_repo.create(
        pet_id=mochi.id, name="Clip nails",
        note=None, duration=15,
        priority="Preferred", recurrence="Monthly",
        scheduled_date=today, preferred_time=time(10, 0),
    )
    task_repo.create(
        pet_id=bruno.id, name="Brush coat",
        note=None, duration=20,
        priority="Low", recurrence="Weekly",
        scheduled_date=today, preferred_time=time(9, 0),
    )
    task_repo.create(
        pet_id=bruno.id, name="Evening walk",
        note=None, duration=45,
        priority="Essential", recurrence="Daily",
        scheduled_date=today, preferred_time=time(17, 0),
    )

    # Mark "Morning walk" and "Clip nails" as completed before printing.
    task_repo.mark_complete(morning_walk.id)
    task_repo.mark_complete(clip_nails.id)

    # ── Generate schedule ──────────────────────────────────────────────────────
    scheduler = Scheduler(task_repo=task_repo, availability_repo=avail_repo)
    results = scheduler.generate_schedule(owner_id=owner.id, query_date=today)

    day_name = today.strftime("%A, %B %-d, %Y")
    print(f"\nSchedule for {day_name}")

    # 1. Unsorted
    print_results(results, pet_repo, "1. All tasks (unsorted)")

    # 2. Sorted earliest to latest
    sorted_results = scheduler.sort_by_scheduled_time(results)
    print_results(sorted_results, pet_repo, "2. All tasks (sorted by time)")

    # 3. Incomplete tasks only
    incomplete = scheduler.filter_tasks(results, completed=False)
    incomplete = scheduler.sort_by_scheduled_time(incomplete)
    print_results(incomplete, pet_repo, "3. Incomplete tasks only")

    # 4. Bruno's tasks only
    bruno_tasks = scheduler.filter_tasks(results, pet_id=bruno.id)
    bruno_tasks = scheduler.sort_by_scheduled_time(bruno_tasks)
    print_results(bruno_tasks, pet_repo, f"4. Bruno's tasks only")

    print()


if __name__ == "__main__":
    main()
