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


def print_sorted_and_filtered_views(scheduler: Scheduler) -> None:
	print(f"\n{scheduler.pet.name} - Sorted by duration (ascending):")
	for idx, task in enumerate(scheduler.sort_by_duration(), start=1):
		status = "done" if task.is_done else "pending"
		print(f"  {idx}. {task.name} | {task.duration_minutes} min | {status}")

	pending = scheduler.filter_tasks(is_done=False)
	done = scheduler.filter_tasks(is_done=True)
	matching_pet = scheduler.filter_tasks(pet_name=scheduler.pet.name)
	non_matching_pet = scheduler.filter_tasks(pet_name="NotMyPet")

	print("  Pending tasks:", [task.name for task in pending])
	print("  Done tasks:", [task.name for task in done])
	print("  Pet-name match count:", len(matching_pet))
	print("  Pet-name mismatch count:", len(non_matching_pet))


def print_conflict_detection(scheduler: Scheduler) -> None:
	result = scheduler.detect_conflicts()
	print(f"\n{scheduler.pet.name} - Conflict Detection:")
	
	conflicts = result.get("conflicts", [])
	warnings = result.get("warnings", [])
	
	if conflicts:
		print(f"  ⚠️ Found {len(conflicts)} time conflict(s):")
		for task_a, task_b in conflicts:
			start_a = getattr(task_a, "start_time", "N/A")
			end_a = getattr(task_a, "start_time", "N/A")
			start_b = getattr(task_b, "start_time", "N/A")
			print(f"    • {task_a.name} ({start_a}, {task_a.duration_minutes} min) overlaps with {task_b.name} ({start_b}, {task_b.duration_minutes} min)")
	else:
		print("  ✓ No conflicts detected.")
	
	if warnings:
		print(f"  ⚠️ Issues encountered during check:")
		for warning in warnings:
			print(f"    • {warning}")
	else:
		print("  ✓ All tasks have valid scheduling data.")


def main() -> None:
	owner = Owner(name="Jordan", available_minutes=90)

	dog = Pet(name="Mochi", species="dog", age=4, notes="Needs evening walk.")
	cat = Pet(name="Luna", species="cat", age=2, notes="Playful in the morning.")

	dog_scheduler = Scheduler(owner=owner, pet=dog)
	cat_scheduler = Scheduler(owner=owner, pet=cat)

	# Add tasks intentionally out of duration order.
	dog_scheduler.add_task(Task("Vet call", "health", 5, 2))
	dog_scheduler.add_task(Task("Morning walk", "exercise", 30, 3))
	dog_scheduler.add_task(Task("Breakfast", "feeding", 15, 3))

	cat_scheduler.add_task(Task("Laser play", "enrichment", 20, 1))
	cat_scheduler.add_task(Task("Litter cleanup", "hygiene", 10, 2))
	cat_scheduler.add_task(Task("Medication", "health", 5, 3))

	# Mark one task done so completion-status filters are visible.
	dog_scheduler.tasks[0].mark_done()

	print("Today's Schedule")
	print("=" * 16)
	print(f"Owner: {owner.name}")
	print(f"Available minutes per plan: {owner.available_minutes}")

	print_schedule_for_pet(dog_scheduler)
	print_schedule_for_pet(cat_scheduler)

	print("\nFilter + Sort Checks")
	print("=" * 20)
	print_sorted_and_filtered_views(dog_scheduler)
	print_sorted_and_filtered_views(cat_scheduler)

	# === NEW: Add tasks with overlapping start times and detect conflicts ===
	print("\n" + "=" * 40)
	print("Conflict Detection Test")
	print("=" * 40)

	# Create a new scheduler with tasks at overlapping times
	conflict_pet = Pet(name="Buddy", species="dog", age=3, notes="Test pet")
	conflict_scheduler = Scheduler(owner=owner, pet=conflict_pet)

	# Add tasks with time conflicts
	walk = Task("Morning walk", "exercise", 30, 3)
	walk.start_time = "09:00"
	conflict_scheduler.add_task(walk)

	breakfast = Task("Breakfast", "feeding", 20, 3)
	breakfast.start_time = "09:15"  # Overlaps with walk (09:00-09:30)
	conflict_scheduler.add_task(breakfast)

	play = Task("Play time", "enrichment", 15, 2)
	play.start_time = "09:45"  # No overlap
	conflict_scheduler.add_task(play)

	incomplete = Task("Vet appointment", "health", 30, 3)
	# No start_time set - will trigger warning
	conflict_scheduler.add_task(incomplete)

	# Detect and print conflicts
	print_conflict_detection(conflict_scheduler)


if __name__ == "__main__":
	main()
