from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule_for_pet(scheduler: Scheduler) -> None:
	plan = scheduler.generate_plan()
	print(f"\n{scheduler.pet.name} ({scheduler.pet.species.title()}):")

	if not plan:
		print("  No tasks fit into available time.")
		return

	for idx, task in enumerate(plan, start=1):
		print(
			f"  {idx}. {task.name} | {task.duration_minutes} min | "
			f"priority {task.priority} | {task.category}"
		)


def main() -> None:
	owner = Owner(name="Jordan", available_minutes=90)

	dog = Pet(name="Mochi", species="dog", age=4, notes="Needs evening walk.")
	cat = Pet(name="Luna", species="cat", age=2, notes="Playful in the morning.")

	dog_scheduler = Scheduler(owner=owner, pet=dog)
	cat_scheduler = Scheduler(owner=owner, pet=cat)

	dog_scheduler.add_task(Task("Morning walk", "exercise", 30, 3))
	dog_scheduler.add_task(Task("Breakfast", "feeding", 15, 3))
	cat_scheduler.add_task(Task("Litter cleanup", "hygiene", 10, 2))
	cat_scheduler.add_task(Task("Laser play", "enrichment", 20, 1))

	print("Today's Schedule")
	print("=" * 16)
	print(f"Owner: {owner.name}")
	print(f"Available minutes per plan: {owner.available_minutes}")

	print_schedule_for_pet(dog_scheduler)
	print_schedule_for_pet(cat_scheduler)


if __name__ == "__main__":
	main()
