---
description: Cancel the active TDD loop
allowed-tools: Read(.tdd-state.json:*), Write(.tdd-state.json:*)
---

# /cancel-tdd Command

When the user runs `/cancel-tdd`, follow these instructions:

## Step 1: Check for Active Loop

Try to read `.tdd-state.json`:

- **If file doesn't exist:**
  - Display: "No TDD loop state found. Use `/tdd-loop` to start a new loop."
  - STOP.

- **If file exists but `active: false`:**
  - Display: "TDD loop is not active. It was already completed or cancelled."
  - Display the stopped reason if available: "Reason: <stoppedReason>"
  - STOP.

## Step 2: Cancel the Loop

Update `.tdd-state.json` by setting:
- `active`: false
- `completedAt`: <current ISO timestamp>
- `stoppedReason`: "cancelled_by_user"

Keep all other fields unchanged (preserve history, files, etc.).

## Step 3: Report Cancellation

Display:

```
🛑 **TDD Loop Cancelled**

Completed: <iteration> iteration(s)

Generated Files:
  Tests (<count of testFiles>):
    <list each test file path>

  Implementation (<count of implFiles>):
    <list each impl file path>

Last Phase: <phase>
Last Verdict: <lastVerdict or "None">

State file preserved at: .tdd-state.json
You can review it or delete it manually.
```

**Note:** Files created during the loop remain in your project. Review and modify them as needed.
