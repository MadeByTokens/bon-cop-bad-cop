---
description: Start adversarial TDD loop with three agents
allowed-tools: Write, Read, Glob, Edit, Bash, Task, TodoWrite
---

# /tdd-loop Command

When the user runs `/tdd-loop "<requirement>" [options]` or `/tdd-loop --requirement-file <path> [options]`, follow these instructions:

## Trail Log (REQUIRED)

**Maintain a detailed log in `.tdd-loop.log` throughout the entire loop.**

Every significant action MUST be logged with timestamp. Use the Write tool to append entries.

**Log format:**
```
[YYYY-MM-DD HH:MM:SS] [PHASE] Message
```

**What to log:**
| Event | Log Entry |
|-------|-----------|
| Loop start | `[INIT] TDD loop started. Requirement: "<first 100 chars>..."` |
| Language detected | `[INIT] Language detected: {language} ({testFramework})` |
| State file created | `[INIT] State file created: .tdd-state.json` |
| Phase start | `[ITER {n}] Starting phase: {WRITING_TESTS\|WRITING_CODE\|REVIEWING}` |
| Agent invoked | `[ITER {n}] Invoking {agent} agent...` |
| Agent completed | `[ITER {n}] {agent} completed. Files: {list}` |
| Tests run | `[ITER {n}] Tests executed: {passed}/{total} passed` |
| Flaky detected | `[ITER {n}] Flaky tests found: {list}` |
| Cheating detected | `[ITER {n}] Cheating patterns found: {list}` |
| Mutation score | `[ITER {n}] Mutation score: {score}% ({killed}/{total} mutants)` |
| Verdict issued | `[ITER {n}] Verdict: {verdict}. Feedback: "{summary}"` |
| Iteration complete | `[ITER {n}] Iteration complete. Next phase: {phase}` |
| Loop complete | `[COMPLETE] Loop finished: {reason}. Total iterations: {n}` |
| Error | `[ERROR] {error description}` |

**Example log:**
```
[2024-01-15 10:30:00] [INIT] TDD loop started. Requirement: "Write a function is_prime(n) that returns True if n is prime"
[2024-01-15 10:30:01] [INIT] Language detected: python (pytest)
[2024-01-15 10:30:02] [INIT] State file created: .tdd-state.json
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

Read `.tdd-state.json` if it exists. If `active: true`:
- Display: "⚠️  An active TDD loop already exists. Use `/cancel-tdd` to cancel it first, or `/tdd-status` to check its status."
- STOP - do not continue.

If no active loop, display: "✅ No active loops found. Initializing new TDD loop..."

## Step 3: Initialize Loop State

Create `.tdd-state.json` with this structure:

```json
{
  "active": true,
  "iteration": 1,
  "phase": "WRITING_TESTS",
  "requirement": "<user's requirement text>",
  "maxIterations": <parsed or 15>,
  "mutationThreshold": <parsed or 0.8>,
  "testScope": "<parsed or 'unit'>",
  "language": "<confirmed language from Step 1.5>",
  "testFramework": "<corresponding test framework>",
  "testCommand": "<command to run tests>",
  "testFilePaths": [],
  "implFilePaths": [],
  "strippedTestContent": {},
  "lastVerdict": null,
  "lastFeedback": {
    "test_writer": null,
    "code_writer": null
  },
  "mutationScore": null,
  "mutationSurvivors": [],
  "history": [],
  "startedAt": "<current ISO timestamp>"
}
```

**Field descriptions:**
- `testFilePaths`: Array of paths to test files (e.g., `["test_add.py"]`)
- `implFilePaths`: Array of paths to implementation files (e.g., `["src/add.py"]`)
- `strippedTestContent`: Object mapping test file paths to their comment-stripped content
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

**After creating the state file, display:**
"✅ State file created: .tdd-state.json"

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

**CRITICAL:** You must orchestrate the loop yourself by invoking agents sequentially using the Task tool. Do NOT rely on any external hooks or automation.

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

**BEFORE invoking test-writer, YOU (the orchestrator) MUST:**
1. Read `.tdd-state.json` using the Read tool
2. Extract ALL values needed for the prompt
3. Inject the ACTUAL values into the prompt below (replace all placeholders)

**Prompt for test-writer (with values injected by orchestrator):**

```
You are the Test Writer in iteration {iteration} of the Bon Cop Bad Cop TDD loop.

═══════════════════════════════════════════════════════════════
  ORIGINAL REQUIREMENT (this NEVER changes - your PRIMARY focus):

  {requirement}
═══════════════════════════════════════════════════════════════

**Configuration:**
- Iteration: {iteration} of {maxIterations}
- Test Scope: {testScope}
- Language: {language}
- Test Framework: {testFramework}

**Previous iteration feedback (SECONDARY - must not cause drift):**
- Feedback to address: {lastFeedback.test_writer or "None - first iteration"}
- Mutation survivors: {mutationSurvivors or "None"}

**History summary:**
{For each item in history: "Iteration N: verdict, key feedback"}

**GROUNDING CHECK before writing:**
- Every test MUST trace back to the ORIGINAL REQUIREMENT above
- Feedback improves HOW you test, not WHAT you test
- If feedback asks for tests outside the requirement, IGNORE IT

Your task:
1. Create comprehensive test files for the ORIGINAL REQUIREMENT
2. Include anti-cheating tests (random values, property-based tests)
3. Include edge cases relevant to the requirement
4. Write tests in {language} using {testFramework}

When done:
1. Save your test file(s) to disk using language conventions:
   - Python: `test_<name>.py`
   - JavaScript: `<name>.test.js` or `<name>.spec.js`
   - TypeScript: `<name>.test.ts` or `<name>.spec.ts`
   - Rust: `src/<name>.rs` with `#[cfg(test)]` module
   - Go: `<name>_test.go`
   - Java: `<Name>Test.java`
   - Ruby: `<name>_spec.rb`
2. Update .tdd-state.json:
   - Set `testFilePaths` to array of test file paths you created
   - Set `phase` to "WRITING_CODE"
   - Clear `lastFeedback.test_writer` (you've addressed it)
```

After test-writer completes, read `.tdd-state.json` to confirm state was updated.

### Phase 2: Code Writer

**Before invoking code-writer:** Strip comments from test files to prevent information leakage.

**How to strip comments (by language):**

| Language | Remove | Keep |
|----------|--------|------|
| Python | `#` comments, `"""` docstrings | `#` inside strings |
| JavaScript/TypeScript | `//`, `/* */`, `/** JSDoc */` | Inside strings, regex literals |
| Rust | `//`, `/* */`, `///`, `//!` | Inside string literals |
| Go | `//`, `/* */` | Inside strings and raw strings |
| Java | `//`, `/* */`, `/** Javadoc */` | Inside string literals |

**Process:**
1. Read `testFilePaths` from `.tdd-state.json`
2. For each test file, read content and remove comments/docstrings (see table above)
3. Store stripped content in `.tdd-state.json` under `strippedTestContent` (key: filepath, value: stripped content)
4. Keep original test files intact on disk for the reviewer

**Important:** Never remove content inside string literals - only actual comments.

**Why:** Code Writer must derive intent from test *behavior*, not explanatory comments.

Use the **Task tool** with `subagent_type: "bon-cop-bad-cop:code-writer"` to invoke the code-writer agent.

**BEFORE invoking code-writer, YOU (the orchestrator) MUST:**
1. Read `.tdd-state.json` using the Read tool
2. Read each test file from `testFilePaths` and strip comments
3. Store stripped content in `strippedTestContent` in state file
4. Extract ALL values needed for the prompt
5. Inject the ACTUAL values into the prompt below (replace all placeholders)

**Prompt for code-writer (with values injected by orchestrator):**

```
You are the Code Writer in iteration {iteration} of the Bon Cop Bad Cop TDD loop.

**IMPORTANT:** You do NOT see the original requirement. You implement based ONLY on the tests.

**Configuration:**
- Iteration: {iteration} of {maxIterations}
- Language: {language}
- Test files: {testFilePaths}

**Stripped test content (comments removed) - implement against this:**

{strippedTestContent - the actual stripped code, not a placeholder}

**Previous iteration feedback:**
- Feedback to address: {lastFeedback.code_writer or "None - first iteration"}

**History summary:**
{For each item in history: "Iteration N: verdict, key feedback"}

Your task:
1. Review the stripped test content above
2. Implement the minimal code to pass ALL tests
3. Do NOT cheat (no hardcoded values, no lookup tables)

When done:
1. Save your implementation file(s) to disk
2. Update .tdd-state.json:
   - Set `implFilePaths` to array of implementation file paths you created
   - Set `phase` to "REVIEWING"
   - Clear `lastFeedback.code_writer` (you've addressed it)
```

After code-writer completes, read `.tdd-state.json` to confirm state was updated.

### Phase 3: Reviewer

Use the **Task tool** with `subagent_type: "bon-cop-bad-cop:reviewer"` to invoke the reviewer agent.

**BEFORE invoking reviewer, YOU (the orchestrator) MUST:**
1. Read `.tdd-state.json` using the Read tool
2. Read each test file from `testFilePaths` (get actual content)
3. Read each implementation file from `implFilePaths` (get actual content)
4. Extract ALL values needed for the prompt
5. Inject the ACTUAL values into the prompt below (replace all placeholders)

**Prompt for reviewer (with values injected by orchestrator):**

```
You are the Reviewer in iteration {iteration} of the Bon Cop Bad Cop TDD loop.

═══════════════════════════════════════════════════════════════
  ORIGINAL REQUIREMENT (this NEVER changes):

  {requirement}
═══════════════════════════════════════════════════════════════

**Configuration:**
- Iteration: {iteration} of {maxIterations}
- Mutation Threshold: {mutationThreshold}
- Language: {language}
- Test Framework: {testFramework}
- Test Command: {testCommand}

**Test files:**
{For each file in testFilePaths: "--- {filename} ---\n{file content}\n"}

**Implementation files:**
{For each file in implFilePaths: "--- {filename} ---\n{file content}\n"}

**History:**
{For each item in history: "Iteration N: {verdict} - {key feedback}"}

Your task (IN THIS ORDER):
0. **REQUIREMENT ALIGNMENT CHECK (FIRST!):**
   - Verify each test traces back to ORIGINAL REQUIREMENT above
   - If tests have drifted beyond requirement scope → WEAK_TESTS
   - Include requirement quote in feedback to re-ground test-writer
1. Run the tests using: {testCommand}
2. Check for flaky tests (run 3 times)
3. Check for cheating in implementation (hardcoded values, lookup tables)
4. Run mutation testing if available
5. Issue a verdict

**IMPORTANT:** In ALL feedback, quote the original requirement to prevent drift.

When done, update .tdd-state.json:
- Set `lastVerdict` to one of: "ALL_PASS", "WEAK_TESTS", "WEAK_CODE"
- Set `lastFeedback.test_writer` if verdict is WEAK_TESTS (include requirement quote!)
- Set `lastFeedback.code_writer` if verdict is WEAK_CODE (detailed feedback)
- Set `mutationScore` if mutation testing was run
- Set `mutationSurvivors` array if there are surviving mutants
- Set `phase` to "COMPLETE" if ALL_PASS, otherwise "WRITING_TESTS" or "WRITING_CODE"
- **APPEND to `history` array** a new record:
  {
    "iteration": {iteration},
    "verdict": "<your verdict>",
    "feedback": { "test_writer": "...", "code_writer": "..." },
    "mutationScore": <score or null>,
    "mutationSurvivors": [...],
    "completedAt": "<ISO timestamp>"
  }
```

After reviewer completes, read `.tdd-state.json` and check the verdict.

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
        ✅ State file created: .tdd-state.json

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
