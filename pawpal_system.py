from dataclasses import dataclass, field


@dataclass
class Owner:
	name: str
	available_minutes: int


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

	def mark_done(self):
		pass


@dataclass
class Scheduler:
	owner: Owner
	pet: Pet
	tasks: list[Task] = field(default_factory=list)

	def add_task(self, task: Task):
		pass

	def remove_task(self, task_name: str):
		pass

	def generate_plan(self):
		pass
