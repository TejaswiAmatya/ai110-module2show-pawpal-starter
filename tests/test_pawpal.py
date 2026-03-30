import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pawpal_system import Owner, Pet, Scheduler, Task

"""Tests for the PawPal pet care scheduling system."""
def test_task_completion_changes_status():
	task = Task(
		name="Evening meds",
		category="medication",
		duration_minutes=5,
		priority=3,
	)

	assert task.is_done is False

	# Support either naming convention: mark_complete() or mark_done().
	mark_complete = getattr(task, "mark_complete", task.mark_done)
	mark_complete()

	assert task.is_done is True

"""Tests for the Scheduler class."""
def test_adding_task_increases_pet_task_count():
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	starting_count = len(scheduler.tasks)

	scheduler.add_task(
		Task(
			name="Morning walk",
			category="exercise",
			duration_minutes=20,
			priority=2,
		)
	)

	assert len(scheduler.tasks) == starting_count + 1
