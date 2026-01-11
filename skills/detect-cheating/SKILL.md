---
name: detect-cheating
description: Analyze implementation code for cheating patterns by cross-referencing with test values
---

# Detect Cheating

Systematically analyze implementation code to find patterns where the Code Writer is gaming tests rather than implementing real logic.

## Step 1: Extract Test Values

Read the test file and extract:
- **Input values** passed to functions in test calls
- **Expected outputs** in assertions (assertEqual, expect().toBe(), assert_eq!, etc.)

Record these as pairs: `{input: X, expected: Y}`

## Step 2: Scan Implementation

For each function in the implementation, check for these patterns:

### Pattern A: Hardcoded Returns (HIGH severity)

Look for conditionals that return test values directly:

```python
# Python
if n == 15: return "FizzBuzz"    # Matches test input/output
if a == 2 and b == 3: return 5   # Specific test case
```

```javascript
// JavaScript
if (n === 15) return "FizzBuzz";
if (a === 2 && b === 3) return 5;
```

```java
// Java
if (n == 15) return "FizzBuzz";
```

```rust
// Rust
if n == 15 { return "FizzBuzz"; }
match n { 15 => "FizzBuzz", ... }
```

```c
// C/C++
if (n == 15) return "FizzBuzz";
switch(n) { case 15: return "FizzBuzz"; }
```

**Detection rule:** If the condition contains a test input AND returns the matching test output, flag as hardcoded.

### Pattern B: Lookup Tables (HIGH severity)

Data structures mapping test inputs to outputs:

```python
ANSWERS = {15: "FizzBuzz", 3: "Fizz", 5: "Buzz"}
```

```javascript
const RESULTS = {15: "FizzBuzz", 3: "Fizz"};
const lookup = new Map([[15, "FizzBuzz"]]);
```

**Detection rule:** If ≥2 keys in a dict/map/object match test inputs, flag as lookup table.

### Pattern C: Excessive Conditionals (MEDIUM severity)

Function with many if/elif/else or switch cases matching test values:

**Detection rule:** If a function has >5 conditionals AND most reference test inputs, flag as suspicious.

### Pattern D: Test Environment Detection (HIGH severity)

Code that behaves differently in test context:

```python
if 'pytest' in sys.modules: ...
if os.environ.get('TESTING'): ...
```

```javascript
if (process.env.NODE_ENV === 'test') { ... }
if (typeof jest !== 'undefined') { ... }
if (global.describe) { ... }
```

```java
if (System.getProperty("test.mode") != null) { ... }
```

```rust
#[cfg(test)] // in non-test code
```

```c
#ifdef TESTING
```

## Step 3: Report Findings

For each pattern found, report:

```
[PATTERN_TYPE] line LINE_NUMBER (SEVERITY)
Code: THE_OFFENDING_CODE
Reason: WHY_THIS_IS_CHEATING
```

**Final verdict:**
- **CLEAN** - No patterns found
- **CHEATING DETECTED** - List all findings sorted by severity
