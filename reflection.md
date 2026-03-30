# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Going into this I wasn't totally sure how many classes I needed, but after reading the scenario a few times I landed on four.

**Owner** just holds the pet owner's name and how much time they have each day. **Pet** stores basic profile stuff — name, species, age, and any care notes. **Task** was the one I thought about the most: it has a name, category (like "walk" or "meds"), duration in minutes, a priority number, and an `is_done` flag. It also has a `mark_done()` method so you can track when something gets completed. Then **Scheduler** is the one that ties everything together — it holds a reference to an Owner, a Pet, and a list of Tasks, and it has three main methods: `add_task()`, `remove_task()`, and `generate_plan()`.

The relationships looked like this:

- Owner owns one or more Pets
- Scheduler belongs to one Owner
- Scheduler cares for one Pet
- Scheduler manages zero or more Tasks

**b. Design changes**

Yeah, the design did change. The biggest thing was the Owner-to-Pet relationship. In my original skeleton I had it as one-to-one — one owner, one pet. That felt fine at first, but then I thought about it more and realised that's pretty limiting. Lots of people have more than one pet. So I changed it so an Owner can have a list of Pets instead. Honestly it was a small change in the code but it made the whole design feel a lot more realistic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler ends up juggling a few things at once. The main one is time — each owner has a daily `available_minutes` budget (90 minutes in my demo), and the plan has to fit inside it. Tasks also have a priority from 1 to 3, and if two tasks have the same priority the scheduler breaks the tie by picking the shorter one first. It also only includes tasks that haven't been completed yet, and if a task is daily or weekly, completing it automatically creates the next one.

I decided priority and total time were the most important constraints because that's what actually matters to a pet owner. They don't usually think "I need to walk the dog at exactly 9:15" — they think "I have an hour and a half today, what needs to happen?" Fitting the right things into limited time felt more useful than trying to assign exact clock times.

**b. Tradeoffs**

The main tradeoff I made was between time-budget optimisation and actual clock-time conflict detection. `generate_plan()` just picks the highest-priority tasks that fit within the available minutes — it doesn't care about when in the day they happen. Conflict detection is a completely separate method, `detect_conflicts()`, that you call if you actually want to check for overlapping start times.

So for example: two tasks that together take exactly 90 minutes will both get selected by `generate_plan()`. But if they're both scheduled for 9:00 AM and overlap by 15 minutes, the scheduler doesn't block them — it just returns both. You'd have to call `detect_conflicts()` to find out.

I think this is fine for this use case. Most pet owners aren't building a minute-by-minute timetable. And keeping planning and conflict-checking separate means each one is simpler and easier to test. If I tried to solve both at the same time I'd basically be dealing with the interval scheduling problem, which gets complicated fast.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI in three main ways throughout the project.

The first was test generation. I asked the AI to look at my code and generate edge case tests, and it came back with 58 of them. I'll be honest — I would never have written that many on my own. But going through them made me think about things I hadn't considered, like what happens at month boundaries (March 31 → April 1) or when someone enters an invalid time like "25:00". That was genuinely useful.

The second was debugging. When tests started failing, I'd paste the error into Copilot and ask what was going wrong. One specific example: `detect_conflicts()` wasn't checking whether the hours and minutes were actually valid — it just parsed whatever you gave it. So "25:00" would go through without a complaint. The AI pointed out I needed range checks, and once I added those, the system handled bad input gracefully instead of crashing.

The third was wiring up the Streamlit UI. Connecting the frontend to the backend was honestly more tedious than I expected. I used AI to help generate the plan table, the overflow warning, and the recurrence notifications. It saved a lot of time on the fiddly parts.

**b. Judgment and verification**

There was one moment where I pushed back on the AI. When it generated the test cases, one of them used `assert set(plan) == {task1, task2}` — which assumes Task objects are hashable. Python dataclasses aren't hashable by default unless you set `frozen=True`, so the test just crashed. The AI suggested making Task frozen, but that would've broken `is_done` updates since frozen dataclasses can't be mutated. So instead I changed the assertion to `assert task1 in plan and task2 in plan`. It's a small thing, but it's a good reminder that the AI doesn't always know the specific constraints of your design.

For verification I mostly just ran the tests. If they passed, the suggestion was probably good. For the UI I launched the app and clicked around to see if things actually behaved the way I expected. I also re-read the scheduler code occasionally to make sure I wasn't accidentally duplicating logic in `app.py`.

---

## 4. Testing and Verification

**a. What you tested**

I ended up with 58 tests across six areas, which felt like a lot but I think each one earned its place.

**Recurring tasks (8 tests)** — marking daily and weekly tasks complete, chaining completions across multiple days, crossing date boundaries like Dec 31 → Jan 1, and checking that one-time tasks don't accidentally regenerate.

**Sorting by duration (6 tests)** — basic ascending order, tied durations keeping insertion order, single tasks, empty lists, mixed completed/pending tasks, and extreme durations (1 minute up to 1440).

**Conflict detection (10 tests)** — this one had the most edge cases. Boundary touches (09:30 end vs 09:30 start shouldn't count as a conflict), midnight boundaries, invalid formats like "25:00" or "12:60" or "12:30:00", tasks missing a start time altogether, and three-way overlaps.

**Filtering (7 tests)** — pet names with extra whitespace, case-insensitive matching, filtering by `is_done`, combined filters, special characters in names.

**Input validation (4 tests)** — negative duration, zero duration, negative priority, invalid frequency strings, and absurdly large values like 999999 minutes.

**Plan generation (9 tests)** — zero available time, exact time fit, priority ordering, tie-breaking by duration, all tasks already completed, and overflow detection.

The reason these mattered is that bugs in the scheduler don't just look bad — they actually affect the pet owner's day. If recurrence breaks at month boundaries, a daily medication reminder won't get rescheduled. If conflict detection crashes on a typo, the app goes down instead of just warning the user. Testing this stuff early meant I caught those problems in tests instead of in the actual app.

**b. Confidence**

Honestly? About a 3 out of 5. All 58 tests pass, which is reassuring, but I know that's not the full picture.

The tests cover inputs I thought of. They don't cover inputs I didn't think of — like Unicode characters in task names, or what happens if someone sets priority to 999. I also didn't test concurrent UI interactions, like clicking "Complete task" twice before the page refreshes. And the time-conflict detection is separate from planning by design, but that does mean a user could have a plan that looks fine on paper but has overlapping tasks in practice. The system warns them, but it doesn't stop them.

I also haven't tested this with a real user. That's a whole different kind of confidence.

---

## 5. Reflection

**a. What went well**

The thing I'm most happy with is the recurring task logic. When a task gets marked done, `mark_done()` either returns a new Task (for daily or weekly tasks) or `None` (for one-time tasks). The scheduler then just appends that new Task to the list if there is one. It's simple, it works, and it handles month and year boundaries without needing any special cases for February or leap years. I wasn't sure it would be that clean when I started writing it.

I'm also glad I wrote as many tests as I did. Having 58 tests that all pass doesn't mean the app is perfect, but it does mean I understand what my code is actually doing. And writing them forced me to define what "correct" even means for each method, which made me a better designer.

**b. What you would improve**

A few things are sitting in the back of my mind. First, input validation is pretty weak right now — you can add a task with a name that's just spaces and it'll go through fine. That should probably be rejected.

Second, and this is a big one: the app doesn't persist any data. Refresh the page and everything disappears. A real version would save to a database. Even SQLite would be fine for a local tool.

Third, `generate_plan()` tells you _which_ tasks fit in your day, but not _when_ to do them. It'd be more useful if it actually assigned start times. That's harder — it gets into interval scheduling — but I think it's the feature that would make the app feel most complete.

I'd also want to handle multi-pet households better. Right now you switch between pets with a dropdown, which works, but a tabbed layout showing tasks per pet side by side would be much cleaner.

**c. Key takeaway**

The biggest thing I took away from this project is that specific prompts are way more useful than vague ones. "Generate test cases for recurring tasks at month boundaries" got me something I could use. "Make the tests better" got me nothing.

That same idea applies to design. I started out vaguely thinking about "building a scheduler" and not making much progress. Once I narrowed it down to "fit the highest-priority tasks into the owner's daily time budget and warn if they go over," things clicked. A specific, humble goal that you can actually finish beats a clever ambitious one that you can't.

The other thing — and I didn't expect this one — is that being honest about tradeoffs in the design actually made the system _better_, not worse. Separating `generate_plan()` from `detect_conflicts()` felt like admitting I wasn't solving the full problem. But it made both methods simpler, easier to test, and easier to explain. Hiding a tradeoff doesn't make it go away. It just means it surprises someone later.
