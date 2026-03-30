
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

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=1440, value=90
)
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

# Keep this pet object updated from current form inputs
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

st.markdown("### Tasks")
st.caption("Add tasks using the scheduler backend.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

priority_map = {"low": 1, "medium": 2, "high": 3}

if st.button("Add task"):
    if not task_title.strip():
        st.error("Task title cannot be empty.")
    else:
        try:
            scheduler.add_task(
                Task(
                    name=task_title.strip(),
                    category="general",
                    duration_minutes=int(duration),
                    priority=priority_map[priority],
                )
            )
            st.success("Task added to scheduler.")
        except ValueError as exc:
            st.error(str(exc))

if scheduler.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.name,
                "category": task.category,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "is_done": task.is_done,
            }
            for task in scheduler.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate today's plan using your backend scheduler logic.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if not plan:
        st.warning("No tasks fit within the available minutes.")
    else:
        st.success(f"Today's Schedule for {scheduler.pet.name}")
        total_minutes = 0
        for index, task in enumerate(plan, start=1):
            total_minutes += task.duration_minutes
            st.write(
                f"{index}. {task.name} ({task.duration_minutes} min, priority {task.priority})"
            )
        st.caption(
            f"Planned time: {total_minutes}/{scheduler.owner.available_minutes} minutes"
        )
