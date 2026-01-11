---
name: detect-flaky
description: Run tests multiple times and identify non-deterministic tests by comparing results
---

# Detect Flaky Tests

Run the test suite 3 times and systematically compare results to identify non-deterministic tests.

## Step 1: Identify Test Framework

Check for these files to determine the framework:

| Check | Framework | Test Command |
|-------|-----------|--------------|
| `pytest.ini` or `test_*.py` | pytest | `pytest -v --tb=no` |
| `jest.config.*` or `*.test.js` | Jest | `npx jest --verbose` |
| `Cargo.toml` with `[dev-dependencies]` | cargo | `cargo test -- --nocapture` |
| `pom.xml` | Maven/JUnit | `mvn test -q` |
| `go.mod` and `*_test.go` | Go | `go test -v ./...` |
| `package.json` with vitest | Vitest | `npx vitest run` |
| `*.rb` and `Gemfile` with rspec | RSpec | `bundle exec rspec --format documentation` |

**IMPORTANT:** Use verbose flags (`-v`, `--verbose`) to get individual test names.

## Step 2: Run Tests 3 Times

Execute the test command 3 times, capturing output for each run:

```
Run 1: [execute test command]
Run 2: [execute test command]
Run 3: [execute test command]
```

For each run, extract a list of test results:
- Test name/identifier
- Result: PASS, FAIL, ERROR, SKIP

## Step 3: Parse Test Output

### pytest output format:
```
test_module.py::test_name PASSED
test_module.py::test_other FAILED
```

### Jest output format:
```
✓ test name (10 ms)
✕ other test (5 ms)
```

### cargo test output format:
```
test test_name ... ok
test test_other ... FAILED
```

### Go test output format:
```
--- PASS: TestName (0.00s)
--- FAIL: TestOther (0.01s)
```

### JUnit/Maven output format:
Look for `Tests run:` summary or parse `target/surefire-reports/*.xml`

## Step 4: Compare Results

Create a table of test results across all 3 runs:

```
Test Name           | Run 1 | Run 2 | Run 3 | Status
--------------------|-------|-------|-------|--------
test_deterministic  | PASS  | PASS  | PASS  | STABLE
test_async_bug      | PASS  | FAIL  | PASS  | FLAKY
test_race_condition | FAIL  | PASS  | FAIL  | FLAKY
```

**A test is FLAKY if:** Results differ across any of the 3 runs.

## Step 5: Report Findings

**If all tests are consistent:**
```
STABLE
All tests produced identical results across 3 runs.
Total: N tests checked
```

**If flaky tests found:**
```
FLAKY TESTS DETECTED

test_async_operation: PASS, FAIL, PASS
test_timing_dependent: PASS, PASS, FAIL

Recommendation: Fix these tests before proceeding.
Common causes: unseeded randomness, race conditions, shared state.
```
