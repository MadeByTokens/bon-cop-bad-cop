---
description: Start adversarial TDD loop with three agents
allowed-tools: Write, Read, Glob, Edit, Bash, Task, TodoWrite, Skill
---

# /tdd-loop Command

When the user runs `/tdd-loop "<requirement>" [options]` or `/tdd-loop --requirement-file <path> [options]`, follow these instructions:

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
  "testFiles": {},
  "implFiles": {},
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

**Prompt for test-writer:**
```
You are the Test Writer in iteration <iteration> of the Bon Cop Bad Cop TDD loop.

**Requirement:** <requirement from state>
**Test Scope:** <testScope>

**Language:** <language from state>
**Test Framework:** <testFramework from state>

Your task:
1. Create comprehensive test files for this requirement
2. Include anti-cheating tests (random values, property-based tests)
3. Include edge cases and boundary conditions
4. Write tests in the confirmed language using the specified test framework

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
   - Set `testFiles` to include your test files (key: filename, value: content)
   - Set `phase` to "WRITING_CODE"

<If there's feedback from previous iteration>
**Previous feedback:** <lastFeedback.test_writer>
**Mutation survivors to address:** <mutationSurvivors>
</If>
```

After test-writer completes, read `.tdd-state.json` to confirm state was updated.

### Phase 2: Code Writer

**Before invoking code-writer:** Strip comments from test files to prevent information leakage.

1. For each test file, use the **strip-comments** skill
2. The skill removes all comments, docstrings, and documentation
3. Save or hold the stripped content (do not modify original test files)
4. Pass ONLY the stripped test content to code-writer
5. Keep original test files intact for the reviewer

**Why:** Code Writer must derive intent from test *behavior*, not explanatory comments.

Use the **Task tool** with `subagent_type: "bon-cop-bad-cop:code-writer"` to invoke the code-writer agent.

**Prompt for code-writer:**
```
You are the Code Writer in iteration <iteration> of the Bon Cop Bad Cop TDD loop.

**IMPORTANT:** You do NOT see the original requirement. You must implement based ONLY on the tests.

**Language:** <language from state>
**Test files to implement against:**
<List test files from state>

Your task:
1. Read the test files (focus on what they test, not comments)
2. Implement the minimal code to pass ALL tests
3. Do NOT cheat (no hardcoded values, no lookup tables)

When done:
1. Save your implementation file(s) to disk
2. Update .tdd-state.json:
   - Set `implFiles` to include your implementation files
   - Set `phase` to "REVIEWING"

<If there's feedback from previous iteration>
**Previous feedback:** <lastFeedback.code_writer>
</If>
```

After code-writer completes, read `.tdd-state.json` to confirm state was updated.

### Phase 3: Reviewer

Use the **Task tool** with `subagent_type: "bon-cop-bad-cop:reviewer"` to invoke the reviewer agent.

**Prompt for reviewer:**
```
You are the Reviewer in iteration <iteration> of the Bon Cop Bad Cop TDD loop.

**Original Requirement:** <requirement>
**Mutation Threshold:** <mutationThreshold>
**Language:** <language from state>
**Test Command:** <testCommand from state>

**Test files:** <list from testFiles>
**Implementation files:** <list from implFiles>

Your task:
1. Run the tests using the test command and check they pass
2. Check for flaky tests (run multiple times if needed)
3. Check for cheating in implementation (hardcoded values, lookup tables)
4. Run mutation testing if available
5. Issue a verdict

When done, update .tdd-state.json:
- Set `lastVerdict` to one of: "ALL_PASS", "WEAK_TESTS", "WEAK_CODE"
- Set `lastFeedback.test_writer` if verdict is WEAK_TESTS (what to improve)
- Set `lastFeedback.code_writer` if verdict is WEAK_CODE (what to fix)
- Set `mutationScore` if mutation testing was run
- Set `mutationSurvivors` if there are surviving mutants
- Set `phase` to "COMPLETE" if ALL_PASS, otherwise "WRITING_TESTS" or "WRITING_CODE"
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
