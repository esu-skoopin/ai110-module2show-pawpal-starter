# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Schedule for Friday, July 3, 2026

TIME     TASK               PET      PRIORITY
--------------------------------------------------
08:00    Morning walk       Bruno    Essential
08:30    Feed breakfast     Mochi    Essential
         Note: Feed 1/4 cup kibble
09:00    Brush coat         Bruno    Low
10:00    Clip nails         Mochi    Preferred
17:00    Evening walk       Bruno    Essential
```

## 🧪 Testing PawPal+

Command to run the full test suite:
```bash
python3 -m pytest
```

The tests in my project cover the following areas:
- Basic tests
    - Whether adding a task for a pet increases the task count for the same pet
    - Whether calling `mark_complete()` for a task sets `task.completed` to `True`
- Whether sorting tasks by scheduled time works as expected
- Whether filtering tasks by completion status and/or pet works as expected
- Whether `mark_complete()` creates the next instance of a task, as appropriate, depending on whether the task is recurring or not

Sample test output:

```
tests/test_pawpal.py .......                                [100%]

======================= 13 passed in 0.12s =======================
```

Confidence level: ⭐️⭐️⭐️⭐️⭐️
<blockquote>
<details>
  <summary><i>&nbsp;What does "confidence level" refer to?</i></summary>
  <p></p>
  <p><i>This metric describes how confident the code author is about the reliability of the system, based on the results of the existing tests, out of 5 stars</i></p>
</details>
</blockquote>

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_by_scheduled_time()` | Sort tasks by scheduled time |
| Filtering | `filter_tasks()` | Filter tasks by completion status and/or pet |
| Recurring tasks | `mark_complete()` | Able to handle tasks that repeat daily, weekly, monthly and yearly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
