# PawPal+ Project Reflection

## 1. System Design

**a. Three core actions**
- Identify three core actions a user should be able to perform
	Users should be able to add/edit their own info
	Users should be able to add/edit the info for their pet(s) (e.g., name, type of animal, breed, etc.)
	Users should be able to add/edit the types of pet care tasks needed for their pet. User must enter the name (e.g., walk), duration and priority for each task at minimum.

**b. Initial design**

- Briefly describe your initial UML design.

	My initial UML design includes four classes: Owner, Pet, Task and OwnerAvailability. An owner can have multiple pets and availability records and each pet can have multiple tasks.

- What classes did you include, and what responsibilities did you assign to each?

	- Owner: create owner, get owner, edit owner and delete owner
	- Pet: create pet, get pets by owner, get pet, edit pet and delete pet
	- Task: create task, get task, get tasks by owner by date, get tasks by owner by date range, edit task and delete task
	- OwnerAvailability: create availability, get all availabilities by owner, get all availabilities by owner by day of week, get availability, edit availability and delete availability

**c. Design changes**

- Did your design change during implementation?

	No, the AI tool I'm using (Claude Code) did not find anything that needed to be changed.

- If yes, describe at least one change and why you made it.

	N/A.

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
