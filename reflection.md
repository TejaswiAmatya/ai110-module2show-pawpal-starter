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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
