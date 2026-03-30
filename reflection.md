# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  In the initial UML design, I have 4 core classes:

1. Owner: This includes pet owner's name and available time for pet care
2. Pet: This includes name, species, age, and notes
3. Tasks: This includes name, category (e.g. walk, feed, meds), duration_minutes, priority, and a is_done flag, plus a mark_done() method to track completion.
4. Scheduler: This holds a reference to one Owner, one Pet, and a list<Task>. It exposes three methods: add_task(), remove_task(), and generate_plan(), which produces the daily schedule.

This is how they are related to one other
Owner "1" --> "1.._" Pet : owns
Scheduler "1" --> "1" Owner : belongs to
Scheduler "1" --> "1" Pet : cares for
Scheduler "1" --> "0.._" Task : manages

- What classes did you include, and what responsibilities did you assign to each?

1. Owner: This includes pet owner's name and available time for pet care
2. Pet: This includes name, species, age, and notes
3. Tasks: This includes name, category (e.g. walk, feed, meds), duration_minutes, priority, and a is_done flag, plus a mark_done() method to track completion.
4. Scheduler: This holds a reference to one Owner, one Pet, and a list<Task>. It exposes three methods: add_task(), remove_task(), and generate_plan(), which produces the daily schedule.

**b. Design changes**

- Did your design change during implementation?
  yes
- If yes, describe at least one change and why you made it.
  The skeleton model represented only had a 1 to 1 relation between pet and owner. This meant one owner could only have one pet. This was changed by adding a list for owner.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - **Time:** Total available_minutes per day (90 min in the demo)
  - **Priority:** Tasks are ranked by priority (1-3), then by duration (shorter-first tie-break)
  - **Completion status:** Only pending (not done) tasks are included in plans
  - **Recurrence:** Daily/weekly tasks auto-create next instances when marked done
  - Most important: Priority and total time budget drive all scheduling decisions

- How did you decide which constraints mattered most?
  Pet owners care most about fitting high-priority care (meds, feeding, walks) into their limited daily time. Time priority > task recurrence > exact scheduling.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  **Tradeoff: Time-budget optimization vs. time-conflict avoidance.**
  - `generate_plan()` optimizes for total time spent (picks tasks that fit within available_minutes) but does NOT enforce specific start-times or detect schedule conflicts.
  - Conflict detection (`detect_conflicts()`) is a *separate* check that returns warnings, not something that blocks plan generation.
  - Example: Two tasks totaling 90 minutes fit the budget and are selected, but if they have overlapping start_times (09:00-09:30 and 09:15-09:35), the scheduler still returns both; the user must call `detect_conflicts()` to learn about the overlap.

- Why is that tradeoff reasonable for this scenario?
  1. **Pet owners rarely plan with exact times.** They think "I have 90 minutes today for Mochi" not "walk at 09:00, breakfast at 09:30." Rough time budgets are more practical.
  2. **Keeps the algorithm simple and fast.** O(n log n) priority sort + greedy greedy selection beats trying to solve the NP-hard bin-packing + interval-scheduling problem.
  3. **Conflict detection is optional but available.** Users who *do* schedule by time can run `detect_conflicts()` to validate, then adjust tasks manually.
  4. **Separation of concerns.** Planning (how much time) and conflict-checking (when in the day) are two concerns; keeping them separate makes the system easier to extend later.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
