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
    task_repo.create(
        pet_id=bruno.id, name="Morning walk",
        note=None, duration=30,
        priority="essential", frequency="daily",
        scheduled_date=today, preferred_time=time(8, 0),
    )
    task_repo.create(
        pet_id=mochi.id, name="Feed breakfast",
        note="Feed 1/4 cup kibble", duration=10,
        priority="essential", frequency="daily",
        scheduled_date=today, preferred_time=time(8, 30),
    )
    task_repo.create(
        pet_id=mochi.id, name="Clip nails",
        note=None, duration=15,
        priority="preferred", frequency="monthly",
        scheduled_date=today, preferred_time=time(10, 0),
    )
    task_repo.create(
        pet_id=bruno.id, name="Brush coat",
        note=None, duration=20,
        priority="low", frequency="weekly",
        scheduled_date=today, preferred_time=time(9, 0),
    )
    task_repo.create(
        pet_id=bruno.id, name="Evening walk",
        note=None, duration=45,
        priority="essential", frequency="daily",
        scheduled_date=today, preferred_time=time(17, 0),
    )

    # ── Generate schedule ──────────────────────────────────────────────────────
    scheduler = Scheduler(task_repo=task_repo, availability_repo=avail_repo)
    results = scheduler.generate_schedule(owner_id=owner.id, query_date=today)

    # ── Print ──────────────────────────────────────────────────────────────────
    day_name = today.strftime("%A, %B %-d, %Y")
    print()
    print(f"Schedule for {day_name}")

    scheduled = sorted(
        [r for r in results if r["scheduled"]],
        key=lambda r: r["scheduled_time"],
    )
    unscheduled = [r for r in results if not r["scheduled"]]

    if scheduled:
        print(f"\n{'TIME':<8} {'TASK':<18} {'PET':<8} {'PRIORITY'}")
        print("-" * 50)
        for entry in scheduled:
            task = entry["task"]
            pet = pet_repo.get(task.pet_id)
            pet_name = pet.name if pet else "?"
            t = entry["scheduled_time"].strftime("%H:%M")
            print(f"{t:<8} {task.name:<18} {pet_name:<8} {task.priority.capitalize()}")
            if task.note:
                print(f"{'':8} Note: {task.note}")
    else:
        print("\nNo tasks could be scheduled today.")

    if unscheduled:
        print(f"\nUnscheduled ({len(unscheduled)}):")
        for entry in unscheduled:
            task = entry["task"]
            print(f"• {task.name} — {entry['reason']}")

    print()


if __name__ == "__main__":
    main()
