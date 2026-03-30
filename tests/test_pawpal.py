import sys
from datetime import date
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


def test_filter_tasks_by_completion_status():
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task_done = Task("Breakfast", "feeding", 10, 3)
	task_pending = Task("Walk", "exercise", 20, 2)
	task_done.mark_done()

	scheduler.add_task(task_done)
	scheduler.add_task(task_pending)

	done_tasks = scheduler.filter_tasks(is_done=True)
	pending_tasks = scheduler.filter_tasks(is_done=False)

	assert done_tasks == [task_done]
	assert pending_tasks == [task_pending]


def test_filter_tasks_by_pet_name_case_insensitive():
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Breakfast", "feeding", 10, 3)
	scheduler.add_task(task)

	matching = scheduler.filter_tasks(pet_name="mochi")
	not_matching = scheduler.filter_tasks(pet_name="luna")

	assert matching == [task]
	assert not_matching == []


def test_mark_done_creates_next_daily_task():
	task = Task(
		name="Daily walk",
		category="exercise",
		duration_minutes=20,
		priority=2,
		frequency="daily",
		due_date=date(2026, 3, 30),
	)

	next_task = task.mark_done()

	assert task.is_done is True
	assert next_task is not None
	assert next_task.frequency == "daily"
	assert next_task.is_done is False
	assert next_task.due_date == date(2026, 3, 31)


def test_mark_done_creates_next_weekly_task():
	task = Task(
		name="Weekly grooming",
		category="hygiene",
		duration_minutes=30,
		priority=2,
		frequency="weekly",
		due_date=date(2026, 3, 30),
	)

	next_task = task.mark_done()

	assert task.is_done is True
	assert next_task is not None
	assert next_task.frequency == "weekly"
	assert next_task.due_date == date(2026, 4, 6)


def test_scheduler_mark_task_complete_appends_recurring_task():
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	daily_task = Task(
		name="Medication",
		category="health",
		duration_minutes=5,
		priority=3,
		frequency="daily",
		due_date=date(2026, 3, 30),
	)
	scheduler.add_task(daily_task)

	was_marked = scheduler.mark_task_complete("Medication")

	assert was_marked is True
	assert len(scheduler.tasks) == 2
	assert scheduler.tasks[0].is_done is True
	assert scheduler.tasks[1].is_done is False
	assert scheduler.tasks[1].due_date == date(2026, 3, 31)


def test_detect_conflicts_returns_overlapping_pairs():
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Breakfast", "feeding", 20, 3)
	task3 = Task("Grooming", "hygiene", 15, 1)

	task1.start_time = "09:00"
	task2.start_time = "09:20"
	task3.start_time = "10:00"

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == [(task1, task2)]
	assert result["warnings"] == []


def test_detect_conflicts_handles_missing_start_time():
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Breakfast", "feeding", 20, 3)

	task1.start_time = "09:00"

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == []
	assert len(result["warnings"]) == 1
	assert "no start_time" in result["warnings"][0]


def test_detect_conflicts_handles_invalid_time_format():
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task1.start_time = "invalid"

	scheduler.add_task(task1)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == []
	assert len(result["warnings"]) == 1
	assert "invalid start_time format" in result["warnings"][0]
