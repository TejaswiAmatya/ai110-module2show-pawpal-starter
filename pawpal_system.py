from dataclasses import dataclass, field


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
	is_done: bool = False

	def mark_done(self) -> None:
		self.is_done = True


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

	def generate_plan(self) -> list[Task]:
		"""Generate a schedule of tasks that fit within the owner's available time, prioritizing higher priority tasks."""
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
