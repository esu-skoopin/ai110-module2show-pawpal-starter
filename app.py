import streamlit as st
from datetime import date, time

from repositories.owner_repository import OwnerRepository
from repositories.pet_repository import PetRepository
from repositories.task_repository import TaskRepository
from repositories.availability_repository import AvailabilityRepository
from pawpal_system import Scheduler

# Repos are stateless session_state wrappers; safe to re-instantiate on every run.
owner_repo = OwnerRepository()
pet_repo = PetRepository()
task_repo = TaskRepository()
avail_repo = AvailabilityRepository()

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PRIORITIES = ["Essential", "Preferred", "Low"]
FREQUENCIES = ["Never", "Daily", "Weekly", "Monthly", "Yearly"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ══════════════════════════════════════════════════════════════════════════════
# 1. OWNER
# ══════════════════════════════════════════════════════════════════════════════
st.header("Owner")

owners = owner_repo.get_all()

if not owners:
    with st.form("create_owner"):
        st.write("Create an owner to get started.")
        c1, c2 = st.columns(2)
        first = c1.text_input("First name")
        last = c2.text_input("Last name")
        if st.form_submit_button("Create owner"):
            if first and last:
                owner_repo.create(first_name=first, last_name=last)
                st.rerun()
            else:
                st.error("Both first and last name are required.")
    st.stop()

if len(owners) == 1:
    owner = owners[0]
    st.write(f"**{owner.first_name} {owner.last_name}**")
else:
    options = {f"{o.first_name} {o.last_name}": o for o in owners}
    owner = options[st.selectbox("Select owner", list(options.keys()))]

# ══════════════════════════════════════════════════════════════════════════════
# 2. PETS
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Pets")

pets = pet_repo.get_by_owner(owner.id)

if pets:
    for pet in pets:
        label = f"**{pet.name}**"
        if pet.animal_type:
            label += f" — {pet.animal_type}"
        if pet.breed:
            label += f" ({pet.breed})"
        st.write(label)
else:
    st.info("No pets yet. Add one below.")

with st.expander("Add a pet"):
    with st.form("add_pet"):
        c1, c2, c3 = st.columns(3)
        p_name = c1.text_input("Name")
        p_type = c2.text_input("Animal type (optional)")
        p_breed = c3.text_input("Breed (optional)")
        if st.form_submit_button("Add pet"):
            if p_name:
                pet_repo.create(owner_id=owner.id, name=p_name,
                                animal_type=p_type, breed=p_breed or None)
                st.rerun()
            else:
                st.error("Pet name is required.")

# ══════════════════════════════════════════════════════════════════════════════
# 3. AVAILABILITY
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Availability")

windows = avail_repo.get_by_owner(owner.id)

if windows:
    st.table([
        {
            "Day": DAYS[w.day_of_week],
            "Start": w.start_time.strftime("%H:%M") if w.start_time else "—",
            "End": w.end_time.strftime("%H:%M") if w.end_time else "—",
        }
        for w in sorted(windows, key=lambda w: (w.day_of_week, w.start_time or time(0, 0)))
    ])
else:
    st.info("No availability windows yet. Add one below.")

with st.expander("Add an availability window"):
    with st.form("add_availability"):
        c1, c2, c3 = st.columns(3)
        a_day = c1.selectbox("Day", DAYS)
        a_start = c2.time_input("Start", value=time(8, 0))
        a_end = c3.time_input("End", value=time(12, 0))
        if st.form_submit_button("Add window"):
            if a_start < a_end:
                avail_repo.create(owner_id=owner.id, day_of_week=DAYS.index(a_day),
                                  start_time=a_start, end_time=a_end)
                st.rerun()
            else:
                st.error("End time must be after start time.")

# ══════════════════════════════════════════════════════════════════════════════
# 4. TASKS
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Tasks")

schedule_date = st.date_input("Date", value=date.today())

if not pets:
    st.warning("Add a pet before adding tasks.")
else:
    tasks = task_repo.get_by_owner_by_date(owner.id, schedule_date)

    if tasks:
        for task in tasks:
            pet = pet_repo.get(task.pet_id)
            pet_name = pet.name if pet else "?"
            icon = "✅" if task.completed else "⬜"
            pref = (f" · preferred {task.preferred_time.strftime('%H:%M')}"
                    if task.preferred_time else "")
            st.write(f"{icon} **{task.name}** — {pet_name} | "
                     f"{task.priority} | {task.duration} min{pref}")
            if task.note:
                st.caption(f"   {task.note}")
    else:
        st.info(f"No tasks for {schedule_date.strftime('%A, %B %-d')}.")

    with st.expander("Add a task"):
        with st.form("add_task"):
            c1, c2 = st.columns(2)
            t_name = c1.text_input("Task name")
            t_pet = c2.selectbox("Pet", [p.name for p in pets])

            c3, c4, c5 = st.columns(3)
            t_duration = c3.number_input("Duration (min)", min_value=1, max_value=480, value=30)
            t_priority = c4.selectbox("Priority", PRIORITIES)
            t_recurrence = c5.selectbox("Repeats", FREQUENCIES)

            t_note = st.text_input("Note (optional)")

            c6, c7 = st.columns(2)
            use_pref = c6.checkbox("Set preferred time")
            # Time input is always rendered; its value is only used when the checkbox is checked.
            t_preferred = c7.time_input("Preferred time", value=time(9, 0))

            if st.form_submit_button("Add task"):
                if t_name:
                    selected_pet = next(p for p in pets if p.name == t_pet)
                    task_repo.create(
                        pet_id=selected_pet.id,
                        name=t_name,
                        note=t_note or None,
                        duration=int(t_duration),
                        priority=t_priority,
                        recurrence=t_recurrence,
                        scheduled_date=schedule_date,
                        preferred_time=t_preferred if use_pref else None,
                    )
                    st.rerun()
                else:
                    st.error("Task name is required.")

# ══════════════════════════════════════════════════════════════════════════════
# 5. GENERATE SCHEDULE
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Generate Schedule")

if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(task_repo=task_repo, availability_repo=avail_repo)
    st.session_state["schedule_results"] = scheduler.generate_schedule(
        owner_id=owner.id, query_date=schedule_date
    )
    st.session_state["schedule_for_date"] = schedule_date

if "schedule_results" in st.session_state:
    results = st.session_state["schedule_results"]
    result_date = st.session_state["schedule_for_date"]

    scheduled = sorted(
        [r for r in results if r["scheduled"]],
        key=lambda r: r["scheduled_time"],
    )
    unscheduled = [r for r in results if not r["scheduled"]]

    st.subheader(f"{result_date.strftime('%A, %B %-d, %Y')}")

    if scheduled:
        st.table([
            {
                "Time": r["scheduled_time"].strftime("%H:%M"),
                "Task": r["task"].name,
                "Pet": (pet_repo.get(r["task"].pet_id).name
                        if pet_repo.get(r["task"].pet_id) else "?"),
                "Priority": r["task"].priority.capitalize(),
                "Duration": f"{r['task'].duration} min",
            }
            for r in scheduled
        ])
        with st.expander("View explanations"):
            for r in scheduled:
                st.write(f"**{r['task'].name}**: {r['reason']}")
    else:
        st.info("No tasks could be scheduled. Check that tasks exist for this date "
                "and availability windows cover this day of the week.")

    if unscheduled:
        st.warning(f"{len(unscheduled)} task(s) could not be scheduled:")
        for r in unscheduled:
            st.write(f"• **{r['task'].name}**: {r['reason']}")
