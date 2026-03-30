
from pathlib import Path
import sys

import streamlit as st

# Ensure local project modules are importable when launched via Streamlit.
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from pawpal_system import Owner, Pet, Task, Scheduler


def get_or_create_vault_object(key: str, factory):
    if "vault" not in st.session_state:
        st.session_state.vault = {}

    vault = st.session_state.vault
    if key in vault:
        return vault[key]

    vault[key] = factory()
    return vault[key]


def format_task_rows(tasks: list[Task]) -> list[dict]:
    return [
        {
            "task name": task.name,
            "category": task.category,
            "start time": task.start_time or "—",
            "duration (min)": task.duration_minutes,
            "priority": task.priority,
            "frequency": task.frequency,
            "due date": task.due_date.isoformat(),
            "done": task.is_done,
        }
        for task in tasks
    ]


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown("Pet care planning assistant — manage tasks, build daily plans, and detect scheduling conflicts.")

st.divider()

# ── Owner & Pet setup ────────────────────────────────────────────────────────
st.subheader("Owner & Pet")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Available minutes today", min_value=1, max_value=1440, value=90
    )
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Pet age", min_value=0, max_value=40, value=3)
    pet_notes = st.text_input("Pet notes (optional)", value="")

owner = get_or_create_vault_object(
    "owner", lambda: Owner(name=owner_name, available_minutes=int(available_minutes))
)
owner.name = owner_name
owner.available_minutes = int(available_minutes)

normalized_name = pet_name.strip().lower()
pet_key = f"pet:{normalized_name}"

pet = get_or_create_vault_object(
    pet_key,
    lambda: Pet(
        name=pet_name.strip(),
        species=species,
        age=int(pet_age),
        notes=pet_notes,
    ),
)

pet.name = pet_name.strip()
pet.species = species
pet.age = int(pet_age)
pet.notes = pet_notes

if pet not in owner.pets:
    owner.pets.append(pet)

scheduler = get_or_create_vault_object(
    f"scheduler:{normalized_name}", lambda: Scheduler(owner=owner, pet=pet)
)
scheduler.owner = owner
scheduler.pet = pet
if pet not in scheduler.owner.pets:
    scheduler.owner.pets.append(pet)

st.divider()

# ── Add Task ─────────────────────────────────────────────────────────────────
st.subheader("Add Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
    category = st.text_input("Category", value="exercise")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col3:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    start_time_input = st.text_input("Start time (HH:MM, optional)", value="", placeholder="e.g. 08:00")

priority_map = {"low": 1, "medium": 2, "high": 3}

if st.button("Add task"):
    if not task_title.strip():
        st.error("Task title cannot be empty.")
    else:
        start_time_val = start_time_input.strip() if start_time_input.strip() else None
        # Validate HH:MM format if provided
        valid_time = True
        if start_time_val:
            try:
                h, m = start_time_val.split(":")
                if not (0 <= int(h) < 24 and 0 <= int(m) < 60):
                    raise ValueError
            except (ValueError, AttributeError):
                st.error("Start time must be in HH:MM format (e.g. 08:30).")
                valid_time = False

        if valid_time:
            try:
                new_task = Task(
                    name=task_title.strip(),
                    category=category.strip() or "general",
                    duration_minutes=int(duration),
                    priority=priority_map[priority],
                    frequency=frequency,
                    start_time=start_time_val,
                )
                scheduler.add_task(new_task)
                st.success(f"Task '{task_title.strip()}' added.")
            except ValueError as exc:
                st.error(str(exc))

st.divider()

# ── Task feedback (shown after rerun) ────────────────────────────────────────
if "task_feedback" in st.session_state:
    feedback = st.session_state.pop("task_feedback")
    level = feedback.get("level")
    message = feedback.get("message", "")
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "info":
        st.info(message)
    elif level == "error":
        st.error(message)

# ── Filter Tasks ──────────────────────────────────────────────────────────────
st.subheader("Filter Tasks")
st.caption("Uses `Scheduler.filter_tasks()` — filter by completion status.")

filter_status = st.radio(
    "Show tasks by status",
    options=["All", "Pending only", "Completed only"],
    horizontal=True,
)

is_done_map = {"All": None, "Pending only": False, "Completed only": True}
filtered_tasks = scheduler.filter_tasks(is_done=is_done_map[filter_status])

if filtered_tasks:
    st.dataframe(format_task_rows(filtered_tasks), use_container_width=True)
else:
    st.info("No tasks match this filter.")

# Shortcuts used elsewhere
pending_tasks = scheduler.filter_tasks(is_done=False)
completed_tasks = scheduler.filter_tasks(is_done=True)

st.divider()

# ── Mark Task Complete ────────────────────────────────────────────────────────
st.subheader("Mark Task Complete")
st.caption("Uses `Scheduler.mark_task_complete()` — auto-schedules next occurrence for recurring tasks.")

if pending_tasks:
    pending_task_names = [task.name for task in pending_tasks]
    selected_task_name = st.selectbox(
        "Select a pending task to complete",
        options=pending_task_names,
        key=f"complete-task:{normalized_name}",
    )

    if st.button("Complete selected task"):
        before_count = len(scheduler.tasks)
        was_marked = scheduler.mark_task_complete(selected_task_name)
        after_count = len(scheduler.tasks)

        if not was_marked:
            st.session_state["task_feedback"] = {
                "level": "warning",
                "message": "Task not found or already completed.",
            }
        elif after_count > before_count:
            st.session_state["task_feedback"] = {
                "level": "info",
                "message": f"Marked '{selected_task_name}' complete. Next occurrence scheduled.",
            }
        else:
            st.session_state["task_feedback"] = {
                "level": "success",
                "message": f"Marked '{selected_task_name}' as complete.",
            }
        st.rerun()
else:
    st.info("No pending tasks to complete.")

st.divider()

# ── Remove Task ───────────────────────────────────────────────────────────────
st.subheader("Remove Task")
st.caption("Uses `Scheduler.remove_task()` — permanently removes a task by name.")

all_tasks = scheduler.tasks
if all_tasks:
    all_task_names = [task.name for task in all_tasks]
    task_to_remove = st.selectbox(
        "Select task to remove",
        options=all_task_names,
        key=f"remove-task:{normalized_name}",
    )
    if st.button("Remove task"):
        removed = scheduler.remove_task(task_to_remove)
        if removed:
            st.success(f"Task '{task_to_remove}' removed.")
            st.rerun()
        else:
            st.warning("Task not found.")
else:
    st.info("No tasks to remove.")

st.divider()

# ── Sort by Duration ──────────────────────────────────────────────────────────
st.subheader("Sort by Duration")
st.caption("Uses `Scheduler.sort_by_duration()` — shows all tasks ordered from shortest to longest.")

if scheduler.tasks:
    sorted_by_duration = scheduler.sort_by_duration()
    st.dataframe(format_task_rows(sorted_by_duration), use_container_width=True)
    st.caption(f"Quickest task: **{sorted_by_duration[0].name}** ({sorted_by_duration[0].duration_minutes} min)")
else:
    st.info("No tasks to sort.")

st.divider()

# ── Detect Conflicts ──────────────────────────────────────────────────────────
st.subheader("Detect Conflicts")
st.caption("Uses `Scheduler.detect_conflicts()` — finds overlapping task time slots (requires start times).")

if st.button("Run conflict detection"):
    result = scheduler.detect_conflicts()
    conflicts = result["conflicts"]
    warnings = result["warnings"]

    if warnings:
        with st.expander(f"Warnings ({len(warnings)} task(s) skipped — no start time set)", expanded=True):
            for w in warnings:
                st.warning(w)

    if conflicts:
        st.error(f"Found {len(conflicts)} conflict(s):")
        for task_a, task_b in conflicts:
            st.markdown(
                f"- **{task_a.name}** ({task_a.start_time}, {task_a.duration_minutes} min) "
                f"overlaps with **{task_b.name}** ({task_b.start_time}, {task_b.duration_minutes} min)"
            )
    elif not warnings:
        st.success("No conflicts detected — all timed tasks fit without overlap.")
    else:
        st.success("No conflicts among tasks with start times.")

st.divider()

# ── Daily Plan ────────────────────────────────────────────────────────────────
st.subheader("Daily Plan")
st.caption("Uses `Scheduler.generate_plan()` — greedy scheduler that maximizes priority within your time budget.")

plan = scheduler.generate_plan()
plan_sorted = sorted(plan, key=lambda task: (-task.priority, task.name.lower()))

if plan_sorted:
    st.dataframe(format_task_rows(plan_sorted), use_container_width=True)
else:
    st.warning("No tasks fit within the available minutes, or all tasks are done.")

total_scheduled_minutes = sum(task.duration_minutes for task in plan_sorted)
total_pending_minutes = sum(task.duration_minutes for task in pending_tasks)
available = scheduler.owner.available_minutes

if total_pending_minutes <= available:
    st.success(
        f"All pending tasks fit in budget: {total_pending_minutes}/{available} minutes."
    )
else:
    over_budget = total_pending_minutes - available
    pending_by_priority = sorted(
        pending_tasks,
        key=lambda task: (-task.priority, task.duration_minutes, task.name.lower()),
    )
    used_minutes = 0
    overflow_tasks: list[Task] = []
    for task in pending_by_priority:
        if used_minutes + task.duration_minutes <= available:
            used_minutes += task.duration_minutes
        else:
            overflow_tasks.append(task)

    low_priority_overflow = [task.name for task in overflow_tasks if task.priority == 1]
    if not low_priority_overflow:
        low_priority_overflow = [task.name for task in overflow_tasks]

    overflow_text = ", ".join(low_priority_overflow) if low_priority_overflow else "none"
    st.warning(
        f"Today's tasks are {over_budget} minutes over budget. "
        f"Overflow tasks: {overflow_text}."
    )

st.caption(f"Planned: {total_scheduled_minutes} min / {available} min available")

with st.expander("Show completed tasks", expanded=False):
    if completed_tasks:
        st.dataframe(format_task_rows(completed_tasks), use_container_width=True)
    else:
        st.caption("No completed tasks yet.")
