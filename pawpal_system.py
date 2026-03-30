from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Owner:
	name: str
	available_minutes: int
	pets: list["Pet"] = field(default_factory=list)


@dataclass
class Pet:
	name: str
	species: str
	age: int
	notes: str


@dataclass
class Task:
	name: str
	category: str
	duration_minutes: int
	priority: int
	frequency: str = "once"
	due_date: date = field(default_factory=date.today)
	is_done: bool = False
	start_time: str | None = None  # Optional HH:MM format for conflict detection

	def __post_init__(self):
		valid_frequencies = {"once", "daily", "weekly"}
		if self.frequency not in valid_frequencies:
			raise ValueError("Task frequency must be one of: once, daily, weekly.")

	def mark_done(self) -> "Task | None":
		self.is_done = True

		if self.frequency == "daily":
			next_due_date = self.due_date + timedelta(days=1)
		elif self.frequency == "weekly":
			next_due_date = self.due_date + timedelta(days=7)
		else:
			return None

		return Task(
			name=self.name,
			category=self.category,
			duration_minutes=self.duration_minutes,
			priority=self.priority,
			frequency=self.frequency,
			due_date=next_due_date,
			start_time=self.start_time,
		)


@dataclass
class Scheduler:
	"""Manages scheduling of tasks for one pet based on owner's available time and task priorities."""

	owner: Owner
	pet: Pet
	tasks: list[Task] = field(default_factory=list)

	def __post_init__(self):
		if self.pet not in self.owner.pets:
			self.owner.pets.append(self.pet)

	def add_task(self, task: Task) -> None:
		"""Add a task after basic input validation."""
		if task.duration_minutes <= 0:
			raise ValueError("Task duration must be greater than 0 minutes.")
		if task.priority < 0:
			raise ValueError("Task priority must be 0 or greater.")

		self.tasks.append(task)

	def remove_task(self, task_name: str) -> bool:
		"""Remove a task by name. Returns True if removed, False if not found."""
		for idx, task in enumerate(self.tasks):
			if task.name == task_name:
				del self.tasks[idx]
				return True
		return False

	def mark_task_complete(self, task_name: str) -> bool:
		"""Mark a task complete and auto-create its next recurrence if applicable.
		
		Searches for the first pending task by name, marks it done, and if the task has
		a recurring frequency (daily/weekly), automatically creates and appends the next
		instance with the appropriate due date.
		
		Args:
			task_name: The exact name of the task to complete.
		
		Returns:
			True if a task was found and marked complete; False otherwise.
		
		Example:
			scheduler.mark_task_complete("Daily walk")
			# Marks first pending "Daily walk" task as done and creates tomorrow's instance.
		"""
		for task in self.tasks:
			if task.name == task_name and not task.is_done:
				next_task = task.mark_done()
				if next_task is not None:
					self.tasks.append(next_task)
				return True
		return False

	def sort_by_duration(self) -> list[Task]:
		"""Sort all tasks by duration in ascending order.
		
		Useful for quick-win scheduling or viewing tasks from fastest to slowest.
		
		Returns:
			List of all tasks sorted by duration_minutes (ascending). Done and pending tasks included.
		
		Example:
			fast_tasks = scheduler.sort_by_duration()[:3]  # Top 3 quickest tasks
		"""
		return sorted(self.tasks, key=lambda task: task.duration_minutes)

	def filter_tasks(
		self, is_done: bool | None = None, pet_name: str | None = None
	) -> list[Task]:
		"""Filter tasks by completion status and/or pet name.
		
		Allows flexible querying: view pending tasks, completed tasks, or verify tasks belong
		to this pet. Supports both filters simultaneously.
		
		Args:
			is_done: If True, return only completed tasks. If False, return only pending tasks.
			         If None (default), completion status is not filtered.
			pet_name: If provided, return tasks only if pet_name matches this scheduler's pet
			          (case-insensitive). If mismatch, returns empty list.
		
		Returns:
			Filtered list of tasks. Empty list if pet_name doesn't match or no tasks satisfy filter.
		
		Example:
			pending = scheduler.filter_tasks(is_done=False)  # All pending tasks
			done = scheduler.filter_tasks(is_done=True)       # All completed tasks
			buddy_tasks = scheduler.filter_tasks(pet_name="Buddy")  # Check if Buddy owns these tasks
		"""
		if pet_name is not None and self.pet.name.strip().lower() != pet_name.strip().lower():
			return []

		if is_done is None:
			return list(self.tasks)

		return [task for task in self.tasks if task.is_done is is_done]

	def detect_conflicts(self) -> dict:
		"""Detect overlapping task time slots and return conflicts + diagnostic warnings.
		
		Parses start_time (HH:MM format) and duration_minutes for each task, identifies
		any time intervals that overlap, and collects warnings for missing or malformed
		times without crashing. This enables safe conflict-checking even with incomplete data.
		
		Returns:
			A dict with two keys:
			  - "conflicts": list[tuple[Task, Task]] of overlapping task pairs.
			  - "warnings": list[str] of issues encountered (missing/invalid times).
			
		Algorithm:
			O(n log n) sorting + O(n²) pairwise overlap check. Tasks without start_time
			are skipped gracefully and logged.
			
		Example:
			result = scheduler.detect_conflicts()
			if result["conflicts"]:
			    print(f"Found {len(result['conflicts'])} overlap(s)")
			if result["warnings"]:
			    for w in result["warnings"]:
			        print(f"Note: {w}")
		"""
		intervals: list[tuple[int, int, Task]] = []
		warnings: list[str] = []

		for task in self.tasks:
			start_time = getattr(task, "start_time", None)
			if start_time is None:
				warnings.append(f"Task '{task.name}' has no start_time; skipping from conflict check.")
				continue

			try:
				hours_str, minutes_str = start_time.split(":")
				hours = int(hours_str)
				minutes = int(minutes_str)
				if not (0 <= hours < 24 and 0 <= minutes < 60):
					raise ValueError
				start_minutes = hours * 60 + minutes
				end_minutes = start_minutes + task.duration_minutes
				intervals.append((start_minutes, end_minutes, task))
			except (ValueError, IndexError):
				warnings.append(f"Task '{task.name}' has invalid start_time format '{start_time}'; skipping from conflict check.")
				continue

		intervals.sort(key=lambda item: item[0])
		conflicts: list[tuple[Task, Task]] = []

		for i in range(len(intervals)):
			start_i, end_i, task_i = intervals[i]
			for j in range(i + 1, len(intervals)):
				start_j, end_j, task_j = intervals[j]
				if start_j >= end_i:
					break
				if start_i < end_j and start_j < end_i:
					conflicts.append((task_i, task_j))

		return {"conflicts": conflicts, "warnings": warnings}

	def generate_plan(self) -> list[Task]:
		"""Generate a prioritized daily schedule that fits within owner's time budget.
		
		Selects pending tasks in order of priority (highest first), with duration as a
		tie-breaker to fit as many high-value tasks as possible within available_minutes.
		This is a greedy O(n log n) approach that prioritizes importance over optimization.
		
		Returns:
			List of tasks selected for today's schedule, ordered by selection priority.
			May be empty if no tasks fit or all tasks are done.
			
		Note:
			Does NOT check for time-slot conflicts (use detect_conflicts() separately).
			Optimizes for time-budget fit, not clock-time accuracy.
			
		Example:
			today_plan = scheduler.generate_plan()
			for i, task in enumerate(today_plan, 1):
			    print(f"{i}. {task.name} ({task.duration_minutes} min)")
		"""
		remaining_time = self.owner.available_minutes
		plan: list[Task] = []

		pending_tasks = [task for task in self.tasks if not task.is_done]
		sorted_tasks = sorted(
			pending_tasks,
			key=lambda task: (-task.priority, task.duration_minutes, task.name.lower()),
		)

		for task in sorted_tasks:
			if task.duration_minutes <= remaining_time:
				plan.append(task)
				remaining_time -= task.duration_minutes

		return plan
