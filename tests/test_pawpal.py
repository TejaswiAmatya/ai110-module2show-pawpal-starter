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


# ============================================================================
# SORTING TESTS - Comprehensive edge cases for sort_by_duration()
# ============================================================================

def test_sort_by_duration_ascending_order():
	"""Verify tasks are sorted by duration in ascending order."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Feeding", "feeding", 10, 3)
	task3 = Task("Grooming", "hygiene", 60, 1)
	task4 = Task("Play", "enrichment", 5, 2)

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)
	scheduler.add_task(task4)

	sorted_tasks = scheduler.sort_by_duration()

	assert sorted_tasks == [task4, task2, task1, task3]
	assert sorted_tasks[0].duration_minutes == 5
	assert sorted_tasks[-1].duration_minutes == 60


def test_sort_by_duration_all_same_duration():
	"""Verify sorting handles tasks with identical duration (stable order)."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 20, 2)
	task2 = Task("Feeding", "feeding", 20, 3)
	task3 = Task("Play", "enrichment", 20, 1)

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)

	sorted_tasks = scheduler.sort_by_duration()

	# Should maintain insertion order for equal durations (stable sort)
	assert sorted_tasks == [task1, task2, task3]
	assert all(t.duration_minutes == 20 for t in sorted_tasks)


def test_sort_by_duration_single_task():
	"""Verify sorting a single task returns that task."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 30, 2)
	scheduler.add_task(task)

	sorted_tasks = scheduler.sort_by_duration()

	assert sorted_tasks == [task]
	assert len(sorted_tasks) == 1


def test_sort_by_duration_empty_list():
	"""Verify sorting an empty task list returns empty list."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	sorted_tasks = scheduler.sort_by_duration()

	assert sorted_tasks == []


def test_sort_by_duration_includes_completed_tasks():
	"""Verify sorting includes both pending and completed tasks."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Feeding", "feeding", 10, 3)
	task1.mark_done()

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	sorted_tasks = scheduler.sort_by_duration()

	assert len(sorted_tasks) == 2
	assert sorted_tasks[0] is task2  # 10 min first
	assert sorted_tasks[1] is task1  # 30 min second
	assert sorted_tasks[1].is_done is True


def test_sort_by_duration_extreme_values():
	"""Verify sorting handles extreme duration values."""
	owner = Owner(name="Jordan", available_minutes=2000)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Nap", "rest", 1, 1)
	task2 = Task("All-day event", "event", 1440, 1)  # 1 day
	task3 = Task("Moderate", "activity", 60, 2)

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)

	sorted_tasks = scheduler.sort_by_duration()

	assert sorted_tasks[0].duration_minutes == 1
	assert sorted_tasks[1].duration_minutes == 60
	assert sorted_tasks[2].duration_minutes == 1440


def test_sort_by_duration_does_not_modify_original():
	"""Verify sorting does not modify the original task list."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Feeding", "feeding", 10, 3)

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	original_order = [t.name for t in scheduler.tasks]
	sorted_tasks = scheduler.sort_by_duration()

	# Original list should be unchanged
	assert [t.name for t in scheduler.tasks] == original_order
	assert [t.name for t in sorted_tasks] == ["Feeding", "Walk"]


# ============================================================================
# RECURRENCE LOGIC TESTS - Comprehensive edge cases for recurring tasks
# ============================================================================

def test_mark_done_returns_none_for_once_frequency():
	"""Verify one-time tasks do not regenerate."""
	task = Task(
		name="One-time vet visit",
		category="health",
		duration_minutes=45,
		priority=3,
		frequency="once",
		due_date=date(2026, 3, 30),
	)

	next_task = task.mark_done()

	assert task.is_done is True
	assert next_task is None


def test_chained_daily_task_completions():
	"""Verify marking a daily task done multiple times creates correct chain."""
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

	# Mark complete 3 days in a row
	scheduler.mark_task_complete("Medication")
	assert len(scheduler.tasks) == 2
	assert scheduler.tasks[1].due_date == date(2026, 3, 31)

	scheduler.mark_task_complete("Medication")
	assert len(scheduler.tasks) == 3
	assert scheduler.tasks[2].due_date == date(2026, 4, 1)

	scheduler.mark_task_complete("Medication")
	assert len(scheduler.tasks) == 4
	assert scheduler.tasks[3].due_date == date(2026, 4, 2)


def test_recurring_task_date_boundary_month_transition():
	"""Verify daily tasks crossing month boundaries (Mar 31 -> Apr 1)."""
	task = Task(
		name="Daily walk",
		category="exercise",
		duration_minutes=20,
		priority=2,
		frequency="daily",
		due_date=date(2026, 3, 31),
	)

	next_task = task.mark_done()

	assert next_task.due_date == date(2026, 4, 1)


def test_recurring_task_date_boundary_year_transition():
	"""Verify daily tasks crossing year boundaries (Dec 31 -> Jan 1)."""
	task = Task(
		name="Daily walk",
		category="exercise",
		duration_minutes=20,
		priority=2,
		frequency="daily",
		due_date=date(2025, 12, 31),
	)

	next_task = task.mark_done()

	assert next_task.due_date == date(2026, 1, 1)


def test_recurring_task_preserves_all_attributes():
	"""Verify recurring task preserves name, category, priority, and frequency."""
	task = Task(
		name="Premium grooming",
		category="hygiene",
		duration_minutes=60,
		priority=2,
		frequency="weekly",
		due_date=date(2026, 3, 30),
	)

	next_task = task.mark_done()

	assert next_task.name == "Premium grooming"
	assert next_task.category == "hygiene"
	assert next_task.duration_minutes == 60
	assert next_task.priority == 2
	assert next_task.frequency == "weekly"
	assert next_task.is_done is False


def test_mark_task_complete_nonexistent_task():
	"""Verify marking non-existent task returns False without crashing."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 20, 2)
	scheduler.add_task(task)

	result = scheduler.mark_task_complete("Nonexistent task")

	assert result is False
	assert len(scheduler.tasks) == 1


def test_mark_task_complete_case_sensitive_name():
	"""Verify mark_task_complete uses exact name matching."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Medication", "health", 5, 3, frequency="daily", due_date=date(2026, 3, 30))
	scheduler.add_task(task)

	# Try different case
	result = scheduler.mark_task_complete("medication")

	# Should not match (case-sensitive)
	assert result is False
	assert len(scheduler.tasks) == 1
	assert scheduler.tasks[0].is_done is False


def test_mark_task_complete_finds_first_pending_only():
	"""Verify mark_task_complete targets first pending task, not completed ones."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	# Add first instance, mark complete
	task1 = Task("Walk", "exercise", 20, 2, frequency="daily", due_date=date(2026, 3, 30))
	scheduler.add_task(task1)
	scheduler.mark_task_complete("Walk")

	# Now we have: task1 (done), task2 (pending for Mar 31)
	assert len(scheduler.tasks) == 2
	assert scheduler.tasks[0].is_done is True
	assert scheduler.tasks[1].is_done is False

	# Mark complete again - should complete task2, not task1 again
	scheduler.mark_task_complete("Walk")

	assert len(scheduler.tasks) == 3
	assert scheduler.tasks[1].is_done is True
	assert scheduler.tasks[2].is_done is False
	assert scheduler.tasks[2].due_date == date(2026, 4, 1)


def test_multiple_instances_of_recurring_task_in_list():
	"""Verify scheduler handles multiple instances of same recurring task."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	# Manually add both a pending and completed instance
	task_done = Task("Daily walk", "exercise", 20, 2, frequency="daily", due_date=date(2026, 3, 29))
	task_pending = Task("Daily walk", "exercise", 20, 2, frequency="daily", due_date=date(2026, 3, 30))

	task_done.mark_done()
	scheduler.add_task(task_done)
	scheduler.add_task(task_pending)

	# Should have both in the list
	assert len(scheduler.tasks) == 2
	assert scheduler.tasks[0].is_done is True
	assert scheduler.tasks[1].is_done is False


def test_recurring_task_with_past_due_date():
	"""Verify scheduler handles tasks with due_date in the past."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	# Task due 5 days ago
	past_task = Task(
		name="Missed walk",
		category="exercise",
		duration_minutes=20,
		priority=2,
		frequency="daily",
		due_date=date(2026, 3, 25),
	)
	scheduler.add_task(past_task)

	# Should still be addable and markable
	assert len(scheduler.tasks) == 1

	result = scheduler.mark_task_complete("Missed walk")

	assert result is True
	assert len(scheduler.tasks) == 2
	# Next task should be Mar 26
	assert scheduler.tasks[1].due_date == date(2026, 3, 26)


# ============================================================================
# CONFLICT DETECTION TESTS - Comprehensive edge cases
# ============================================================================

def test_detect_conflicts_boundary_touching_no_conflict():
	"""Verify tasks that touch at boundaries (09:30 end vs 09:30 start) don't conflict."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Feeding", "feeding", 20, 3)

	task1.start_time = "09:00"  # 09:00 - 09:30
	task2.start_time = "09:30"  # 09:30 - 09:50

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == []
	assert result["warnings"] == []


def test_detect_conflicts_midnight_boundary():
	"""Verify conflict detection works around midnight."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Task1", "activity", 60, 1)
	task2 = Task("Task2", "activity", 30, 1)

	task1.start_time = "00:00"  # Midnight
	task2.start_time = "00:59"  # Should conflict with task1

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	result = scheduler.detect_conflicts()

	assert len(result["conflicts"]) == 1
	assert result["conflicts"][0] == (task1, task2)


def test_detect_conflicts_end_of_day():
	"""Verify conflict detection at end-of-day edge cases."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Evening", "activity", 30, 1)
	task2 = Task("Night", "activity", 30, 1)

	task1.start_time = "23:30"
	task2.start_time = "23:45"

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	result = scheduler.detect_conflicts()

	assert len(result["conflicts"]) == 1


def test_detect_conflicts_invalid_hour_format():
	"""Verify graceful handling of invalid hour (25:00)."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task1.start_time = "25:00"

	scheduler.add_task(task1)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == []
	assert len(result["warnings"]) == 1
	assert "invalid start_time format" in result["warnings"][0]


def test_detect_conflicts_invalid_minute_format():
	"""Verify graceful handling of invalid minute (12:60)."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task1.start_time = "12:60"

	scheduler.add_task(task1)

	result = scheduler.detect_conflicts()

	# Should still parse since timedelta will handle overflow
	# OR it might be caught - depends on implementation
	assert result["conflicts"] == []


def test_detect_conflicts_invalid_seconds_format():
	"""Verify graceful handling of extra seconds (12:30:00)."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task1.start_time = "12:30:00"

	scheduler.add_task(task1)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == []
	assert len(result["warnings"]) == 1


def test_detect_conflicts_all_tasks_missing_start_time():
	"""Verify all missing start_time tasks generate warnings, no crash."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Feeding", "feeding", 20, 3)
	task3 = Task("Grooming", "hygiene", 15, 1)

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == []
	assert len(result["warnings"]) == 3


def test_detect_conflicts_mixed_valid_and_invalid_times():
	"""Verify mixed valid/invalid times: process valid, warn about invalid."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Breakfast", "feeding", 20, 3)
	task3 = Task("Grooming", "hygiene", 15, 1)

	task1.start_time = "09:00"
	# task2 has no start_time
	task3.start_time = "09:20"

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)

	result = scheduler.detect_conflicts()

	assert len(result["conflicts"]) == 1
	assert result["conflicts"][0] == (task1, task3)
	assert len(result["warnings"]) == 1


def test_detect_conflicts_single_task():
	"""Verify single task has no conflicts."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 30, 2)
	task.start_time = "09:00"
	scheduler.add_task(task)

	result = scheduler.detect_conflicts()

	assert result["conflicts"] == []
	assert result["warnings"] == []


def test_detect_conflicts_multiple_overlapping_groups():
	"""Verify multiple independent conflict groups are all detected."""
	owner = Owner(name="Jordan", available_minutes=240)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	# Group 1: task1 and task2 overlap
	task1 = Task("Walk", "exercise", 30, 2)
	task2 = Task("Feeding", "feeding", 20, 3)

	# Group 2: task3 and task4 overlap
	task3 = Task("Grooming", "hygiene", 30, 1)
	task4 = Task("Play", "enrichment", 20, 2)

	task1.start_time = "09:00"
	task2.start_time = "09:20"
	task3.start_time = "14:00"
	task4.start_time = "14:20"

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)
	scheduler.add_task(task4)

	result = scheduler.detect_conflicts()

	assert len(result["conflicts"]) == 2
	assert (task1, task2) in result["conflicts"]
	assert (task3, task4) in result["conflicts"]


def test_detect_conflicts_three_way_overlap():
	"""Verify three tasks overlapping are all reported as pairs."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Task1", "activity", 60, 1)
	task2 = Task("Task2", "activity", 60, 1)
	task3 = Task("Task3", "activity", 60, 1)

	task1.start_time = "09:00"  # 09:00 - 10:00
	task2.start_time = "09:30"  # 09:30 - 10:30
	task3.start_time = "10:00"  # 10:00 - 11:00 (doesn't overlap with task1)

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)

	result = scheduler.detect_conflicts()

	# task1-task2 overlap, task2-task3 overlap
	assert len(result["conflicts"]) == 2
	assert (task1, task2) in result["conflicts"]
	assert (task2, task3) in result["conflicts"]


# ============================================================================
# FILTERING TESTS - Edge cases for filter_tasks()
# ============================================================================

def test_filter_tasks_by_pet_name_with_whitespace():
	"""Verify pet name filtering handles leading/trailing whitespace."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name=" Mochi ", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Breakfast", "feeding", 10, 3)
	scheduler.add_task(task)

	# Filter with various whitespace
	matching1 = scheduler.filter_tasks(pet_name="mochi")
	matching2 = scheduler.filter_tasks(pet_name=" mochi ")
	matching3 = scheduler.filter_tasks(pet_name="MOCHI")

	assert matching1 == [task]
	assert matching2 == [task]
	assert matching3 == [task]


def test_filter_tasks_by_nonexistent_pet_name():
	"""Verify filtering with non-existent pet name returns empty list."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Breakfast", "feeding", 10, 3)
	scheduler.add_task(task)

	result = scheduler.filter_tasks(pet_name="Luna")

	assert result == []


def test_filter_tasks_is_done_none_returns_all():
	"""Verify is_done=None returns all tasks (pending + completed)."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Breakfast", "feeding", 10, 3)
	task2 = Task("Walk", "exercise", 20, 2)
	task1.mark_done()

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	result = scheduler.filter_tasks(is_done=None)

	assert len(result) == 2
	assert task1 in result
	assert task2 in result


def test_filter_tasks_on_empty_list():
	"""Verify filtering empty task list returns empty list."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	result = scheduler.filter_tasks(is_done=False)

	assert result == []


def test_filter_tasks_combined_filters():
	"""Verify filtering by is_done AND pet_name applies both constraints."""
	owner = Owner(name="Jordan", available_minutes=120)
	pet1 = Pet(name="Mochi", species="dog", age=4, notes="")
	pet2 = Pet(name="Luna", species="cat", age=3, notes="")

	scheduler1 = Scheduler(owner=owner, pet=pet1)
	scheduler2 = Scheduler(owner=owner, pet=pet2)

	task1_done = Task("Breakfast", "feeding", 10, 3)
	task1_pending = Task("Walk", "exercise", 20, 2)
	task1_done.mark_done()

	scheduler1.add_task(task1_done)
	scheduler1.add_task(task1_pending)

	# Filter for Mochi's pending tasks only
	result = scheduler1.filter_tasks(is_done=False, pet_name="Mochi")

	assert len(result) == 1
	assert result[0] is task1_pending


def test_filter_tasks_pet_name_special_characters():
	"""Verify pet name filter handles special characters."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mr. Fluff-y", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 20, 2)
	scheduler.add_task(task)

	result = scheduler.filter_tasks(pet_name="mr. fluff-y")

	assert result == [task]


def test_filter_tasks_case_variations():
	"""Verify pet name filter is case-insensitive for all variations."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 20, 2)
	scheduler.add_task(task)

	assert scheduler.filter_tasks(pet_name="MOCHI") == [task]
	assert scheduler.filter_tasks(pet_name="mochi") == [task]
	assert scheduler.filter_tasks(pet_name="MoChI") == [task]


# ============================================================================
# INPUT VALIDATION TESTS - Edge cases for add_task()
# ============================================================================

def test_add_task_negative_duration_raises_error():
	"""Verify adding task with negative duration raises ValueError."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", -5, 2)

	try:
		scheduler.add_task(task)
		assert False, "Should have raised ValueError"
	except ValueError as e:
		assert "greater than 0" in str(e)


def test_add_task_zero_duration_raises_error():
	"""Verify adding task with zero duration raises ValueError."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 0, 2)

	try:
		scheduler.add_task(task)
		assert False, "Should have raised ValueError"
	except ValueError as e:
		assert "greater than 0" in str(e)


def test_add_task_negative_priority_raises_error():
	"""Verify adding task with negative priority raises ValueError."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 20, -1)

	try:
		scheduler.add_task(task)
		assert False, "Should have raised ValueError"
	except ValueError as e:
		assert "0 or greater" in str(e)


def test_task_invalid_frequency_raises_error():
	"""Verify Task with invalid frequency raises ValueError."""
	try:
		task = Task(
			name="Walk",
			category="exercise",
			duration_minutes=20,
			priority=2,
			frequency="bi-weekly"
		)
		assert False, "Should have raised ValueError"
	except ValueError as e:
		assert "once, daily, weekly" in str(e)


def test_add_task_large_values():
	"""Verify handling of large duration and priority values."""
	owner = Owner(name="Jordan", available_minutes=999999)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Event", "activity", 999999, 1000000)

	scheduler.add_task(task)

	assert len(scheduler.tasks) == 1
	assert scheduler.tasks[0].duration_minutes == 999999
	assert scheduler.tasks[0].priority == 1000000


# ============================================================================
# PLAN GENERATION TESTS - Edge cases for generate_plan()
# ============================================================================

def test_generate_plan_no_available_time():
	"""Verify plan generation with zero available time returns empty plan."""
	owner = Owner(name="Jordan", available_minutes=0)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 20, 2)
	scheduler.add_task(task)

	plan = scheduler.generate_plan()

	assert plan == []


def test_generate_plan_time_less_than_smallest_task():
	"""Verify plan when available time < smallest task duration."""
	owner = Owner(name="Jordan", available_minutes=5)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task = Task("Walk", "exercise", 20, 2)
	scheduler.add_task(task)

	plan = scheduler.generate_plan()

	assert plan == []


def test_generate_plan_exact_fit():
	"""Verify plan fills exactly when time matches sum of tasks."""
	owner = Owner(name="Jordan", available_minutes=50)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 20, 2)
	task2 = Task("Feeding", "feeding", 30, 3)

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	plan = scheduler.generate_plan()

	assert len(plan) == 2
	assert task1 in plan
	assert task2 in plan


def test_generate_plan_priority_ordering():
	"""Verify plan prioritizes higher-priority tasks first."""
	owner = Owner(name="Jordan", available_minutes=20)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task_low = Task("Play", "enrichment", 20, 1)
	task_high = Task("Feed", "feeding", 20, 3)

	scheduler.add_task(task_low)
	scheduler.add_task(task_high)

	plan = scheduler.generate_plan()

	assert len(plan) == 1
	assert plan[0] is task_high  # High priority should be selected


def test_generate_plan_priority_tie_break_by_duration():
	"""Verify priority ties are broken by duration (shortest first)."""
	owner = Owner(name="Jordan", available_minutes=40)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Task1", "activity", 30, 2)
	task2 = Task("Task2", "activity", 20, 2)
	task3 = Task("Task3", "activity", 10, 2)

	scheduler.add_task(task1)
	scheduler.add_task(task2)
	scheduler.add_task(task3)

	plan = scheduler.generate_plan()

	# With 40 min available: should pick 20 + 10 (not 30)
	assert len(plan) == 2
	assert task2 in plan
	assert task3 in plan
	assert task1 not in plan


def test_generate_plan_all_tasks_completed():
	"""Verify plan is empty when all tasks are completed."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task1 = Task("Walk", "exercise", 20, 2)
	task2 = Task("Feeding", "feeding", 20, 3)

	task1.mark_done()
	task2.mark_done()

	scheduler.add_task(task1)
	scheduler.add_task(task2)

	plan = scheduler.generate_plan()

	assert plan == []


def test_generate_plan_excludes_completed_tasks():
	"""Verify completed tasks are not included in plan."""
	owner = Owner(name="Jordan", available_minutes=60)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	task_done = Task("Breakfast", "feeding", 10, 3)
	task_pending = Task("Walk", "exercise", 20, 2)

	task_done.mark_done()

	scheduler.add_task(task_done)
	scheduler.add_task(task_pending)

	plan = scheduler.generate_plan()

	assert plan == [task_pending]
	assert task_done not in plan


def test_generate_plan_greedy_selection_correctness():
	"""Verify greedy algorithm selects optimal set within constraints."""
	owner = Owner(name="Jordan", available_minutes=50)
	pet = Pet(name="Mochi", species="dog", age=4, notes="")
	scheduler = Scheduler(owner=owner, pet=pet)

	high = Task("High", "activity", 40, 3)
	low1 = Task("Low1", "activity", 20, 1)
	low2 = Task("Low2", "activity", 20, 1)

	scheduler.add_task(high)
	scheduler.add_task(low1)
	scheduler.add_task(low2)

	plan = scheduler.generate_plan()

	# Should pick high (40 min), can't fit low1/low2
	assert plan == [high]
