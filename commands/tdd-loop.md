---
description: Start adversarial TDD loop with three agents
allowed-tools: Write, Read, Glob, Edit, Bash, Task
---

# /tdd-loop Command

When the user runs `/tdd-loop "<requirement>" [options]` or `/tdd-loop --requirement-file <path> [options]`, follow these instructions:

## Trail Log (REQUIRED) - Primary Record

**The `.tdd-loop.log` file is the AUTHORITATIVE record of all loop activity.**

This is critical for context management:
- **Agents write verbose output here**, not to their responses
- **Full mutation survivor details** go here, not in state file
- **Full feedback text** goes here
- **Archived history entries** go here when truncated from state
- The state file and agent responses contain only summaries

Every significant action MUST be logged with timestamp. Use the Write tool to append entries.

**Log format:**
```
[YYYY-MM-DD HH:MM:SS] [PHASE] Message
```

**What to log:**
| Event | Log Entry |
|-------|-----------|
| Plugin version | `[INIT] Bon Cop Bad Cop v{version}` |
| Loop start | `[INIT] TDD loop started. Requirement: "<first 100 chars>..."` |
| Language detected | `[INIT] Language detected: {language} ({testFramework})` |
| State file created | `[INIT] State file created: .tdd-working/state.json` |
| Phase start | `[ITER {n}] Starting phase: {WRITING_TESTS\|WRITING_CODE\|REVIEWING}` |
| Agent invoked | `[ITER {n}] Invoking {agent} agent...` |
| Agent completed | `[ITER {n}] {agent} completed. Files: {list}` |
| Agent verbose output | `[ITER {n}] [{agent}] {detailed analysis, reasoning, progress}` |
| Tests run | `[ITER {n}] Tests executed: {passed}/{total} passed` |
| Flaky detected | `[ITER {n}] Flaky tests found: {list}` |
| Cheating detected | `[ITER {n}] Cheating patterns found: {list}` |
| Mutation score | `[ITER {n}] Mutation score: {score}% ({killed}/{total} mutants)` |
| Mutation survivors | `[ITER {n}] Surviving mutants: {full list of survivors}` |
| Verdict issued | `[ITER {n}] Verdict: {verdict}. Feedback: "{full feedback text}"` |
| Iteration complete | `[ITER {n}] Iteration complete. Next phase: {phase}` |
| History archived | `[HISTORY] Archived iteration {n}: verdict={v}, mutationScore={s}, survivors=[...]` |
| Loop complete | `[COMPLETE] Loop finished: {reason}. Total iterations: {n}` |
| Error | `[ERROR] {error description}` |

**Example log:**
```
[2024-01-15 10:30:00] [INIT] Bon Cop Bad Cop v0.6.0
[2024-01-15 10:30:00] [INIT] TDD loop started. Requirement: "Write a function is_prime(n) that returns True if n is prime"
[2024-01-15 10:30:01] [INIT] Language detected: python (pytest)
[2024-01-15 10:30:02] [INIT] State file created: .tdd-working/state.json
[2024-01-15 10:30:03] [ITER 1] Starting phase: WRITING_TESTS
[2024-01-15 10:30:04] [ITER 1] Invoking test-writer agent...
[2024-01-15 10:31:15] [ITER 1] test-writer completed. Files: test_is_prime.py
[2024-01-15 10:31:16] [ITER 1] Starting phase: WRITING_CODE
[2024-01-15 10:31:17] [ITER 1] Stripping comments from test files...
[2024-01-15 10:31:18] [ITER 1] Invoking code-writer agent...
[2024-01-15 10:32:00] [ITER 1] code-writer completed. Files: is_prime.py
[2024-01-15 10:32:01] [ITER 1] Starting phase: REVIEWING
[2024-01-15 10:32:02] [ITER 1] Invoking reviewer agent...
[2024-01-15 10:32:30] [ITER 1] Tests executed: 12/12 passed
[2024-01-15 10:32:45] [ITER 1] Mutation score: 65% (13/20 mutants killed)
[2024-01-15 10:32:46] [ITER 1] Verdict: WEAK_TESTS. Feedback: "Mutation score below threshold. Survivors: [line 5: changed < to <=]"
[2024-01-15 10:32:47] [ITER 1] Iteration complete. Next phase: WRITING_TESTS
[2024-01-15 10:32:48] [ITER 2] Starting phase: WRITING_TESTS
...
[2024-01-15 10:45:00] [COMPLETE] Loop finished: ALL_PASS. Total iterations: 3
```

**IMPORTANT:** Append to the log file, never overwrite. If the file doesn't exist, create it.

## Context Budget Awareness

This loop can run for many iterations (up to 15 by default). To prevent context exhaustion:

1. **Agent responses are minimal** - Detailed output goes to `.tdd-loop.log`, not responses
2. **History is truncated to 3 iterations** - Older iterations are archived in the log file
3. **State file stays small** - Only current state and recent history
4. **If you need historical details** - Read from `.tdd-loop.log`

**Key principle:** The state file contains *current state*; the log file contains *complete history*.

## Step 0: Initialize

Display: "🎭 Bon Cop Bad Cop v0.6.0"
Log to `.tdd-loop.log`: `[INIT] Bon Cop Bad Cop v0.6.0`

**Note:** When bumping the plugin version, update both `.claude-plugin/plugin.json` AND this file.

## Step 1: Parse User Input

Extract from the command:
- **requirement** (optional): The user's feature description as inline text
- **--requirement-file** (optional): Path to a markdown file containing the requirement
- **--max-iterations** (optional, default: 15): Maximum loop iterations
- **--mutation-threshold** (optional, default: 0.8): Required mutation score (0.0-1.0)
- **--test-scope** (optional, default: "unit"): Test scope (unit/integration/both)
- **--language** (optional, default: auto-detect): Target language

**Requirement source rules:**
- At least one of: inline requirement OR `--requirement-file` must be provided
- If neither is provided, display error: "⚠️ No requirement specified. Provide a quoted requirement or use --requirement-file <path>." and STOP
- Both can be used together: file content becomes the main requirement, inline text is appended as additional notes

**If `--requirement-file` is specified:**
1. Display: "📄 Loading requirement from: <filepath>"
2. Check if the file exists using the Read tool
3. **If the file does not exist or cannot be read:**
   - Display error: "❌ File not found: <filepath>"
   - Display: "Please check the path and try again."
   - STOP - do not continue
4. Read the file content
5. **If the file is empty:**
   - Display error: "❌ Requirement file is empty: <filepath>"
   - STOP - do not continue
6. Display: "✅ Requirement loaded (<N> characters)"

**Combining file and inline requirements:**
If BOTH `--requirement-file` AND inline text are provided, combine them as follows:

```
<file content>

---
**Additional Notes:**
<inline text>
```

Display: "📝 Added inline notes to requirement"

## Step 1.5: Detect and Confirm Language

If `--language` was provided by the user, use that value directly and skip to Step 2.

If `--language` was NOT provided, detect and confirm the language:

### Auto-Detection Rules

Scan the project root for these indicators using Glob:

| Indicator Files | Language | Test Framework | Test Command |
|-----------------|----------|----------------|--------------|
| `pytest.ini`, `pyproject.toml`, `setup.py`, `test_*.py` | Python | pytest | `pytest -v` |
| `jest.config.*`, `*.test.js`, `*.spec.js`, `package.json` (with jest) | JavaScript | Jest | `npx jest --verbose` |
| `vitest.config.*`, `*.test.ts`, `*.spec.ts` | TypeScript | Vitest | `npx vitest run` |
| `Cargo.toml` | Rust | cargo test | `cargo test` |
| `go.mod`, `*_test.go` | Go | go test | `go test -v ./...` |
| `pom.xml`, `build.gradle` | Java | JUnit | `mvn test -q` |
| `Gemfile`, `*_spec.rb` | Ruby | RSpec | `bundle exec rspec` |

### Confirmation with User

Use **AskUserQuestion** to confirm the language:

**If exactly ONE language detected:**
```
Question: "Detected [Language] project. Use this for the TDD loop?"
Header: "Language"
Options:
  1. "[Language] (Recommended)" - Use detected language
  2. "Choose different language" - Show full language list
```

**If MULTIPLE languages detected:**
```
Question: "Multiple languages detected in project. Which should be used for this TDD loop?"
Header: "Language"
Options: [List each detected language] + "Other"
```

**If NO language detected:**
```
Question: "No project language detected. Which language should be used?"
Header: "Language"
Options:
  1. "Python"
  2. "JavaScript/TypeScript"
  3. "Rust"
  4. "Go"
```

### Store Language Configuration

After confirmation, store these values for use throughout the loop:
- `language`: The confirmed language name (e.g., "python", "javascript", "rust")
- `testFramework`: The corresponding test framework (e.g., "pytest", "jest", "cargo")
- `testCommand`: The command to run tests (e.g., "pytest -v", "npx jest --verbose")

Display: "✅ Language confirmed: [Language] (using [testFramework])"

## Step 2: Check for Existing Loop

**IMPORTANT:** First, provide feedback that you're checking:
- Display: "🔍 Checking for existing TDD loops..."

Read `.tdd-working/state.json` if it exists. If `active: true`:
- Display: "⚠️  An active TDD loop already exists. Use `/cancel-tdd` to cancel it first, or `/tdd-status` to check its status."
- STOP - do not continue.

If no active loop, display: "✅ No active loops found. Initializing new TDD loop..."

## Step 3: Create Working Directory and Initialize State

### 3.1 Create Working Directory Structure

Create the `.tdd-working/` directory with the following structure:

```
.tdd-working/
├── inputs/
│   └── requirement.md          # Original requirement (written in 3.2)
├── test-writer/
│   └── status.md               # Agent writes: "DONE" or "BLOCKED: reason"
├── code-writer/
│   └── status.md               # Agent writes: "DONE" or "BLOCKED: reason"
└── reviewer/
    ├── verdict.md              # Agent writes: "ALL_PASS", "WEAK_TESTS", or "WEAK_CODE"
    └── feedback.md             # Agent writes: detailed feedback for next iteration
```

Use Bash to create the directories:
```bash
mkdir -p .tdd-working/inputs .tdd-working/test-writer .tdd-working/code-writer .tdd-working/reviewer
```

### 3.2 Write Requirement File

Write the requirement to `.tdd-working/inputs/requirement.md`:
- This is the ONLY copy of the requirement
- Agents will read from this file, NOT from their prompts

### 3.3 Initialize State File

Create `.tdd-working/state.json` with this structure:

```json
{
  "active": true,
  "iteration": 1,
  "phase": "WRITING_TESTS",
  "maxIterations": <parsed or 15>,
  "mutationThreshold": <parsed or 0.8>,
  "testScope": "<parsed or 'unit'>",
  "language": "<confirmed language from Step 1.5>",
  "testFramework": "<corresponding test framework>",
  "testCommand": "<command to run tests>",
  "testFilePaths": [],
  "implFilePaths": [],
  "lastVerdict": null,
  "mutationScore": null,
  "history": [],
  "startedAt": "<current ISO timestamp>"
}
```

**Note:** The requirement is stored in `.tdd-working/inputs/requirement.md`, NOT in the state file.

**Field descriptions:**
- `testFilePaths`: Array of paths to test files (e.g., `["test_add.py"]`)
- `implFilePaths`: Array of paths to implementation files (e.g., `["src/add.py"]`)
- `history`: Array of iteration records (see below)

**History record structure (appended after each iteration):**
```json
{
  "iteration": 1,
  "verdict": "WEAK_TESTS",
  "feedback": {
    "test_writer": "Add more edge cases...",
    "code_writer": null
  },
  "mutationScore": 0.65,
  "mutationSurvivors": ["line 12: + to -"],
  "completedAt": "<ISO timestamp>"
}
```

**History Management (Context Preservation):**
- Keep only the **last 3 iteration records** in the `history` array
- Before appending a new record, if `history.length >= 3`:
  1. Log the oldest entry's full details to `.tdd-loop.log` with format:
     `[YYYY-MM-DD HH:MM:SS] [HISTORY] Archived iteration N: verdict=X, mutationScore=Y, survivors=[...]`
  2. Remove the oldest entry from the array
  3. Then append the new record
- This keeps the state file small while preserving full history in the log

**History Compression for Older Entries:**
- Current iteration: store full `mutationSurvivors` as array (e.g., `["line 12: + to -", "line 15: < to <="]`)
- Archived iterations (when logged before removal): convert array to count for the log summary

**After creating the working directory and state file, display:**
```
✅ Working directory created: .tdd-working/
✅ Requirement saved to: .tdd-working/inputs/requirement.md
✅ State file created: .tdd-working/state.json
```

## Step 4: Display Loop Initialization

Output:

```
🎭 **Bon Cop Bad Cop - Adversarial TDD Loop**

✓ Loop initialized
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requirement: <requirement>
Language: <language> (<testFramework>)
Max Iterations: <maxIterations>
Mutation Threshold: <mutationThreshold * 100>%
Test Scope: <testScope>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: Test Writer creates comprehensive tests
Phase 2: Code Writer implements based on tests only
Phase 3: Reviewer validates and issues verdict

Loop will continue until ALL_PASS or max iterations reached.
Use /tdd-status to check progress, /cancel-tdd to stop.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 5: Run the TDD Loop

Orchestrate the loop by invoking agents sequentially using the Task tool.

### Loop Algorithm

```
while iteration <= maxIterations:
    1. Invoke test-writer agent (if phase is WRITING_TESTS or verdict is WEAK_TESTS)
    2. Wait for test-writer to complete, update state
    3. Invoke code-writer agent (if phase is WRITING_CODE or verdict is WEAK_CODE)
    4. Wait for code-writer to complete, update state
    5. Invoke reviewer agent
    6. Check verdict:
       - ALL_PASS: Exit loop successfully
       - WEAK_TESTS: Increment iteration, go to step 1
       - WEAK_CODE: Increment iteration, go to step 3
    7. Increment iteration
```

### Phase 1: Test Writer

Use the **Task tool** with `subagent_type: "bon-cop-bad-cop:test-writer"` to invoke the test-writer agent.

**Prompt for test-writer (MINIMAL - agent reads files itself):**

```
You are the Test Writer in iteration {iteration} of {maxIterations}.

**Read your inputs from files:**
- Requirement: `.tdd-working/inputs/requirement.md`
- State/Config: `.tdd-working/state.json`
- Feedback (if iteration > 1): `.tdd-working/reviewer/feedback.md`

**Configuration:** language={language}, testFramework={testFramework}, testScope={testScope}

**Write your outputs:**
- Test files to project root (e.g., `test_*.py`)
- Status to `.tdd-working/test-writer/status.md` (write "DONE")
- Update `.tdd-working/state.json`: set testFilePaths, phase="WRITING_CODE"
- Append to `.tdd-loop.log`

Follow your agent instructions for test writing guidelines.
```

**Note:** The prompt is minimal (~300 bytes). The agent reads requirement and feedback from files.

After test-writer completes, display: `✅ Test Writer completed`

### Phase 2: Code Writer

Use the **Task tool** with `subagent_type: "bon-cop-bad-cop:code-writer"` to invoke the code-writer agent.

**Note:** The Code Writer agent handles comment stripping itself - the orchestrator does NOT strip comments.

**Prompt for code-writer (MINIMAL - agent reads files itself):**

```
You are the Code Writer in iteration {iteration} of {maxIterations}.

**Read your inputs from files:**
- State/Config: `.tdd-working/state.json` (get testFilePaths)
- Test files: Read from testFilePaths array in state file
- Feedback (if lastVerdict was WEAK_CODE): `.tdd-working/reviewer/feedback.md`

**IMPORTANT:** Strip comments from test files before implementing. You do NOT see the requirement.

**Configuration:** language={language}

**Write your outputs:**
- Implementation files to project root
- Status to `.tdd-working/code-writer/status.md` (write "DONE")
- Update `.tdd-working/state.json`: set implFilePaths, phase="REVIEWING"
- Append to `.tdd-loop.log`

Follow your agent instructions for implementation guidelines.
```

**Note:** The prompt is minimal (~400 bytes). The agent reads test files and strips comments itself.

After code-writer completes, display: `✅ Code Writer completed`

### Phase 3: Reviewer

Use the **Task tool** with `subagent_type: "bon-cop-bad-cop:reviewer"` to invoke the reviewer agent.

**Prompt for reviewer (MINIMAL - agent reads files itself):**

```
You are the Reviewer in iteration {iteration} of {maxIterations}.

**Read your inputs from files:**
- Requirement: `.tdd-working/inputs/requirement.md`
- State/Config: `.tdd-working/state.json` (get testFilePaths, implFilePaths)
- Test files: Read from testFilePaths array
- Implementation files: Read from implFilePaths array

**Configuration:** mutationThreshold={mutationThreshold}, testCommand={testCommand}

**Write your outputs:**
- Verdict to `.tdd-working/reviewer/verdict.md` ("ALL_PASS", "WEAK_TESTS", or "WEAK_CODE")
- Feedback to `.tdd-working/reviewer/feedback.md` (for next iteration)
- Update `.tdd-working/state.json`: set lastVerdict, mutationScore, phase, append to history
- Append to `.tdd-loop.log`

Follow your agent instructions for review guidelines.
```

**Note:** The prompt is minimal (~450 bytes). The agent reads requirement, test files, and impl files itself.

After reviewer completes:

1. Read verdict from `.tdd-working/reviewer/verdict.md`
2. Display: `✅ Reviewer completed. Verdict: {lastVerdict}`

### Check Exit Conditions

Read `.tdd-working/state.json` and check:

- If `lastVerdict == "ALL_PASS"` → Go to Step 6 (completion)
- If `iteration >= maxIterations` → Go to Step 6 (max iterations)
- Otherwise → Increment iteration, loop back to Phase 1 or Phase 2 based on verdict:
  - WEAK_TESTS → Phase 1 (test-writer)
  - WEAK_CODE → Phase 2 (code-writer)

## Step 6: Handle Loop Completion

### On ALL_PASS:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 ALL PASS - TDD Loop Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Completed in <iteration> iteration(s)

Generated files:
Tests: <list test files>
Implementation: <list impl files>
Mutation Score: <score>%

The code has been validated against comprehensive tests.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Update state: `active: false`, `stoppedReason: "all_pass"`, `completedAt: <timestamp>`

### On Max Iterations Reached:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  Max iterations (<maxIterations>) reached
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The agents couldn't converge to ALL_PASS within the iteration limit.
Last verdict: <lastVerdict>

Review the generated files and consider:
- Simplifying the requirement
- Increasing max iterations
- Reviewing feedback from last iteration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Update state: `active: false`, `stoppedReason: "max_iterations"`, `completedAt: <timestamp>`

## Progress Updates

Between each agent invocation, display progress:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 Iteration <n>/<max> - Phase: <phase>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Error Handling

If any agent fails or state becomes corrupted:
1. Display error message
2. Set `active: false` and `stoppedReason: "error"`
3. Suggest running `/tdd-status` or `/cancel-tdd`

## Example Full Execution

```
User: /bon-cop-bad-cop:tdd-loop "Write a function add(a, b) that returns the sum"

Claude: 🔍 Scanning project for language indicators...

        [Uses AskUserQuestion]
        Question: "Detected Python project. Use this for the TDD loop?"
        User selects: "Python (Recommended)"

        ✅ Language confirmed: Python (using pytest)

        🔍 Checking for existing TDD loops...
        ✅ No active loops found. Initializing new TDD loop...
        ✅ State file created: .tdd-working/state.json

        🎭 **Bon Cop Bad Cop - Adversarial TDD Loop**
        [... header ...]

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎭 Iteration 1/15 - Phase: WRITING_TESTS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        [Invokes test-writer via Task tool]

        ✅ Test Writer completed. Tests created: test_add.py

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎭 Iteration 1/15 - Phase: WRITING_CODE
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        [Invokes code-writer via Task tool]

        ✅ Code Writer completed. Implementation: add.py

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎭 Iteration 1/15 - Phase: REVIEWING
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        [Invokes reviewer via Task tool]

        ✅ Reviewer verdict: ALL_PASS

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎉 ALL PASS - TDD Loop Complete!
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
