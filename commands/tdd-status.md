---
description: Display current TDD loop status
allowed-tools: Read(.tdd-state.json:*)
---

# /tdd-status Command

When the user runs `/tdd-status`, follow these instructions:

## Step 1: Read State File

Try to read `.tdd-state.json`:

- **If file doesn't exist:**
  Display:
  ```
  📊 **TDD Loop Status**

  Status: No active loop

  No .tdd-state.json found in current directory.

  To start a new loop: /tdd-loop "Your requirement here"
  ```
  STOP.

## Step 2: Parse State Information

Extract from the state file:
- `active` - whether loop is running
- `iteration` - current iteration number
- `maxIterations` - maximum allowed iterations
- `phase` - current phase (WRITING_TESTS/WRITING_CODE/REVIEWING)
- `requirement` - the original requirement
- `testFiles` - object mapping file paths to content
- `implFiles` - object mapping file paths to content
- `lastVerdict` - most recent verdict (WEAK_TESTS/WEAK_CODE/ALL_PASS)
- `lastFeedback` - feedback object
- `mutationScore` - mutation testing score (if available)
- `mutationSurvivors` - array of surviving mutants (if available)
- `startedAt` - when loop started
- `completedAt` - when loop ended (if completed)
- `stoppedReason` - why loop stopped (if stopped)

## Step 3: Display Status

Format and display the status report:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **TDD Loop Status**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: <if active: "🟢 Active" else: "🔴 Inactive (<stoppedReason>)">
Iteration: <iteration> / <maxIterations>
Current Phase: <phase>

Requirement:
  <requirement - first 120 chars><if longer: "...">

Files Generated:
  Tests (<number of testFiles>):
    <list each test file path with "  - " prefix>

  Implementation (<number of implFiles>):
    <list each impl file path with "  - " prefix>

Last Verdict: <lastVerdict or "None yet">

<if mutationScore exists:>
Mutation Score: <mutationScore * 100 rounded to 1 decimal>%
<end if>

<if mutationSurvivors exists and has items:>
Mutation Survivors: <count>
  <list first 3 survivors: "  - Line <line>: <mutation>">
  <if more than 3: "  ... and <count - 3> more">
<end if>

<if lastFeedback.test_writer or lastFeedback.code_writer:>
Last Feedback:
  <if lastFeedback.test_writer: "  To Test Writer: <first 80 chars>...">
  <if lastFeedback.code_writer: "  To Code Writer: <first 80 chars>...">
<end if>

Duration: <calculate time from startedAt to (completedAt or now)>
State file: .tdd-state.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 4: Display Action Hints

At the end, add:

- **If active:**
  ```
  🔄 The loop is running.

  The /tdd-loop command orchestrates agents sequentially.
  Progress will be shown as agents complete their phases.

  Use /cancel-tdd to stop it.
  ```

- **If completed (stoppedReason = "all_pass"):**
  ```
  ✓ Loop completed successfully!
  Review the generated files above.
  ```

- **If cancelled:**
  ```
  Loop was cancelled. Files created so far remain in your project.
  Start a new loop with /tdd-loop if needed.
  ```

- **If max iterations reached:**
  ```
  Max iterations reached. The agents couldn't converge to ALL_PASS.
  Review the files and consider:
  - Simplifying the requirement
  - Starting a new loop with adjusted parameters
  - Manually reviewing and fixing the code
  ```
