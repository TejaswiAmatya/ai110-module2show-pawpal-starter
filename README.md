# PawPal+

## Overview

PawPal+ is a pet care planner that helps busy pet owners organize daily tasks like walks, feeding, medication, and grooming. The app builds a practical daily plan based on your available time and task importance, then shows what fits and what needs to wait. It is designed for non-technical users who want a clear, simple way to stay consistent with pet care.

## Features

- Smart daily planning with priorities:
  The scheduler creates a daily plan by sorting pending tasks by priority (highest first), then by shorter duration, then by name. It uses a greedy approach to fit as many important tasks as possible into the owner's available minutes.
- Duration sorting:
  Tasks can also be sorted from shortest to longest duration for quick-win planning.
- Time budget conflict warning in the UI:
  If all pending tasks fit within the day's time budget, PawPal+ shows a success message. If they do not fit, it shows how many minutes over budget you are and lists the low-priority tasks that are overflowing the plan.
- Recurring task support:
  When a daily task is completed, the next occurrence is automatically created for the following day. When a weekly task is completed, the next occurrence is created 7 days later.
- Instant completion workflow:
  Marking a task complete updates the plan immediately. If a recurring task creates a new occurrence, the app shows an info message so you know it was scheduled.
- Task status filtering:
  The scheduler can return pending tasks, completed tasks, or all tasks. It can also filter by pet name.
- Completed task organization:
  Completed tasks are tucked into an expandable section so the main view stays clean and focused on what is still pending.
- Input safety checks:
  The app rejects invalid task values such as non-positive duration, negative priority, or unsupported recurrence frequency.
- Due-date aware tasks:
  Each task stores a due date, and due dates are shown in the tables.
- Backend conflict detection utility:
  The scheduler can detect overlapping task time windows and return warnings for missing or invalid time formats.

## 📸 Demo

<a href="/course_images/ai110/demo1.png" target="_blank"><img src='/course_images/ai110/demo1.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo2.png" target="_blank"><img src='/course_images/ai110/demo2.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo3.png" target="_blank"><img src='/course_images/ai110/demo3.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo4.png" target="_blank"><img src='/course_images/ai110/demo4.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo5.png" target="_blank"><img src='/course_images/ai110/demo5.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo6.png" target="_blank"><img src='/course_images/ai110/demo6.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo7.png" target="_blank"><img src='/course_images/ai110/demo7.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## How to Run

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Streamlit app:

```bash
streamlit run app.py
```

4. Optional: run tests:

```bash
python -m pytest
```

## Project Structure

```text
.
├── app.py
├── pawpal_system.py
├── tests/
│   └── test_pawpal.py
├── requirements.txt
├── main.py
├── reflection.md
└── README.md
```

- app.py:
  Streamlit user interface. Collects owner and pet inputs, adds tasks, marks tasks complete, shows daily plan tables, and displays budget messages.
- pawpal_system.py:
  Core scheduling engine. Defines Owner, Pet, Task, and Scheduler classes plus all planning, recurrence, filtering, validation, and conflict-detection logic.
- tests/test_pawpal.py:
  Automated tests for planning behavior, recurrence, filtering, sorting, validation, and conflict handling.
- requirements.txt:
  Python dependencies needed to run the app and tests.
- main.py:
  Minimal entry file included with the project scaffold.
- reflection.md:
  Project reflection notes.
