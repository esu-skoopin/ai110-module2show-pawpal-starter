import streamlit as st
from datetime import date, time

from repositories.owner_repository import OwnerRepository
from repositories.pet_repository import PetRepository
from repositories.task_repository import TaskRepository
from repositories.availability_repository import AvailabilityRepository
from pawpal_system import Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Repos are stateless session_state wrappers; safe to re-instantiate on every run.
owner_repo = OwnerRepository()
pet_repo = PetRepository()
task_repo = TaskRepository()
avail_repo = AvailabilityRepository()

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PRIORITIES = ["Essential", "Preferred", "Low"]
FREQUENCIES = ["Never", "Daily", "Weekly", "Monthly", "Yearly"]

# Load global CSS
with open("ui/styles.css") as f:
    st.html(f"<style>{f.read()}</style>")

st.title("🐾 PawPal+")

# ══════════════════════════════════════════════════════════════════════════════
# 1. OWNER
# ══════════════════════════════════════════════════════════════════════════════
st.header("Owner")

owners = owner_repo.get_all()

if not owners:
    with st.form(key="create_owner", enter_to_submit=False):
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
    with st.form(key="add_pet", enter_to_submit=False):
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
    with st.form(key="add_availability", enter_to_submit=False):
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

# Scheduler is instantiated here so it can be shared with section 5.
scheduler = Scheduler(task_repo=task_repo, availability_repo=avail_repo)

if not pets:
    st.warning("Add a pet before adding tasks.")
else:
    tasks = task_repo.get_by_owner_by_date(owner.id, schedule_date)

    if tasks:
        # ── Sort / filter controls ─────────────────────────────────────────
        c_sort, c_status, c_pet = st.columns(3)
        sort_by_time = c_sort.checkbox("Sort by time", key="tasks_sort")
        status_filter = c_status.selectbox(
            "Status", ["All", "Incomplete", "Completed"], key="tasks_status"
        )
        pet_options = ["All pets"] + [p.name for p in pets]
        pet_filter_name = c_pet.selectbox("Pet", pet_options, key="tasks_pet")
        pet_filter_id = next(
            (p.id for p in pets if p.name == pet_filter_name), None
        )

        # Wrap raw Task objects into result dicts so the Scheduler methods can
        # be applied — scheduled_time may be None if scheduling hasn't run yet.
        task_results = [
            {
                "task": t,
                "scheduled_time": t.scheduled_time,
                "scheduled": t.scheduled_time is not None,
                "reason": "",
            }
            for t in tasks
        ]

        completed_arg = (
            None if status_filter == "All" else status_filter == "Completed"
        )
        task_results = scheduler.filter_tasks(
            task_results, completed=completed_arg, pet_id=pet_filter_id
        )
        if sort_by_time:
            task_results = scheduler.sort_by_scheduled_time(task_results)

        # ── Task list ─────────────────────────────────────────────────────
        if task_results:
            for entry in task_results:
                task = entry["task"]
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
            st.info("No tasks match the current filters.")
    else:
        st.info(f"No tasks for {schedule_date.strftime('%A, %B %-d')}.")

    with st.expander("Add a task"):
        with st.form(key="add_task", enter_to_submit=False):
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
    st.session_state["schedule_results"] = scheduler.generate_schedule(
        owner_id=owner.id, query_date=schedule_date
    )
    st.session_state["schedule_for_date"] = schedule_date

if "schedule_results" in st.session_state:
    results = st.session_state["schedule_results"]
    result_date = st.session_state["schedule_for_date"]

    st.subheader(f"{result_date.strftime('%A, %B %-d, %Y')}")

    # ── Sort / filter controls ─────────────────────────────────────────────
    c_sort, c_status, c_pet = st.columns(3)
    sched_sort = c_sort.checkbox("Sort by time", key="sched_sort")
    sched_status = c_status.selectbox(
        "Status", ["All", "Incomplete", "Completed"], key="sched_status"
    )
    sched_pet_options = ["All pets"] + [p.name for p in pets]
    sched_pet_name = c_pet.selectbox("Pet", sched_pet_options, key="sched_pet")
    sched_pet_id = next(
        (p.id for p in pets if p.name == sched_pet_name), None
    )

    completed_arg = (
        None if sched_status == "All" else sched_status == "Completed"
    )
    view = scheduler.filter_tasks(results, completed=completed_arg, pet_id=sched_pet_id)
    if sched_sort:
        view = scheduler.sort_by_scheduled_time(view)

    scheduled = [r for r in view if r["scheduled"]]
    unscheduled = [r for r in view if not r["scheduled"]]

    if scheduled:
        st.table([
            {
                "Time": r["scheduled_time"].strftime("%H:%M"),
                "Task": r["task"].name,
                "Pet": (pet_repo.get(r["task"].pet_id).name
                        if pet_repo.get(r["task"].pet_id) else "?"),
                "Priority": r["task"].priority.capitalize(),
                "Duration": f"{r['task'].duration} min",
                "Done": "✅" if r["task"].completed else "⬜",
            }
            for r in scheduled
        ])
        with st.expander("View explanations"):
            for r in scheduled:
                st.write(f"**{r['task'].name}**: {r['reason']}")
    elif not unscheduled:
        st.info("No tasks match the current filters.")
    else:
        st.info("No tasks could be scheduled. Check that tasks exist for this date "
                "and availability windows cover this day of the week.")

    if unscheduled:
        st.warning(f"{len(unscheduled)} task(s) could not be scheduled:")
        for r in unscheduled:
            st.write(f"• **{r['task'].name}**: {r['reason']}")
