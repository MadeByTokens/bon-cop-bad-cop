![BonCopBadCop](https://github.com/user-attachments/assets/12e2e3d5-3ec7-4ba4-94d7-856f4689a386)

# Bon Cop Bad Cop - Adversarial Test-Driven Development (TDD) Plugin for Claude Code

Three-agent adversarial TDD loop: Test Writer (bad cop), Code Writer (suspect), and Reviewer (good cop) work together while keeping each other honest.

## Installation

### Option A: Via MadeByTokens Marketplace (Recommended)

See https://github.com/MadeByTokens/claude-code-plugins-madebytokens

### Option B: CLI Flag at Launch

```bash
# Clone the repo
git clone https://github.com/MadeByTokens/bon-cop-bad-cop.git

# Launch Claude Code with the plugin directory
claude --plugin-dir /path/to/bon-cop-bad-cop
```

### Option C: Manual Settings Configuration

Clone the repo, then add it to your Claude Code settings file:

**User scope** (`~/.claude/settings.json`):
```json
{
  "pluginDirs": ["/path/to/bon-cop-bad-cop"]
}
```

**Project scope** (`.claude/settings.json` in your project):
```json
{
  "pluginDirs": ["/path/to/bon-cop-bad-cop"]
}
```

## Quick Start

```bash
# Run a TDD loop (after installation)
/bon-cop-bad-cop:tdd-loop "Write a function add(a, b) that returns the sum of a and b"
```

## Example Requirements

Here are simple requirements to test the plugin, ordered by complexity:

### Beginner
```bash
# Prime number checker
/bon-cop-bad-cop:tdd-loop "Write a function is_prime(n) that returns True if n is prime, False otherwise"

# String reversal
/bon-cop-bad-cop:tdd-loop "Write a function reverse_string(s) that returns the reversed string"

# Factorial
/bon-cop-bad-cop:tdd-loop "Write a function factorial(n) that returns n! (n factorial)"
```

### Intermediate
```bash
# Classic FizzBuzz
/bon-cop-bad-cop:tdd-loop "Write a function fizzbuzz(n) that returns 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for both, otherwise the number as a string"

# Email validation
/bon-cop-bad-cop:tdd-loop "Write a function is_valid_email(email) that returns True if the email format is valid"

# Palindrome finder
/bon-cop-bad-cop:tdd-loop "Write a function longest_palindrome(s) that returns the longest palindromic substring"
```

### With Options
```bash
# Override auto-detected language with higher mutation threshold
/bon-cop-bad-cop:tdd-loop "Write a function is_prime(n)" --language rust --mutation-threshold 0.9

# Override to JavaScript with more iterations allowed
/bon-cop-bad-cop:tdd-loop "Write a function reverseString(s)" --language javascript --max-iterations 20
```

## Commands

| Command | Description |
|---------|-------------|
| `/bon-cop-bad-cop:tdd-loop "requirement"` | Start new TDD loop |
| `/bon-cop-bad-cop:tdd-status` | Check current loop status |
| `/bon-cop-bad-cop:cancel-tdd` | Cancel active loop |
| `/bon-cop-bad-cop:help` | Display plugin help and usage |

### Options for tdd-loop

- `--requirement-file path/to/file.md` - Load requirement from markdown file
- `--max-iterations N` - Maximum iterations (default: 15)
- `--mutation-threshold 0.85` - Required mutation score (default: 0.8)
- `--test-scope unit|integration|both` - Test scope (default: unit)
- `--language LANG` - Override auto-detection (python, javascript, typescript, rust, go, java, ruby)

### Using a Requirement File

For complex requirements, create a markdown file and use `--requirement-file`:

```bash
# Create a requirement file with detailed specs
cat > requirement.md << 'EOF'
Write a function `calculate_tax(income, deductions)` that:
- Accepts income as a positive number
- Accepts deductions as a list of {amount, category} objects
- Returns the tax owed based on progressive brackets
- Handles edge cases: zero income, negative values, empty deductions
EOF

# Run TDD loop with the file
/bon-cop-bad-cop:tdd-loop --requirement-file requirement.md

# Or combine with inline notes for run-specific tweaks
/bon-cop-bad-cop:tdd-loop "Focus on edge cases, ignore performance" --requirement-file requirement.md
```

When both are provided, the inline text is appended as "Additional Notes" to the file content.

## How It Works

The plugin orchestrates three specialized agents in sequence:

```mermaid
flowchart TD
    Start([Start TDD Loop]) --> TW

    subgraph TW["Phase 1"]
        TW_Content[<b>Test Writer</b> - Bad Cop<br/>Sees: Requirement, feedback<br/>Creates: Comprehensive tests]
    end

    TW --> CW

    subgraph CW["Phase 2"]
        CW_Content[<b>Code Writer</b> - Suspect<br/>Sees: Tests ONLY<br/>Creates: Implementation]
    end

    CW --> RV

    subgraph RV["Phase 3"]
        RV_Content[<b>Reviewer</b> - Good Cop<br/>Sees: Everything<br/>Runs: Tests + mutation testing]
    end

    RV --> Verdict{Verdict?}

    Verdict -->|WEAK_TESTS| TW
    Verdict -->|WEAK_CODE| CW
    Verdict -->|ALL_PASS| Success([Success!])
```

**Key Innovation:** Each agent runs in isolation with different context. The Code Writer never sees the original requirement - only the tests. This enforces true TDD behavior.

## The Three Agents

### Test Writer (Bad Cop)
- **Role:** Write comprehensive tests that catch cheating
- **Sees:** Requirements, mutation survivors, feedback about tests
- **Never sees:** Implementation code

### Code Writer (Suspect)
- **Role:** Implement code that passes all tests
- **Sees:** Test files only (comments may be stripped)
- **Never sees:** Original requirements

### Reviewer (Good Cop)
- **Role:** Validate both tests and implementation
- **Sees:** Everything
- **Actions:** Run tests, detect flakiness, detect cheating, mutation testing
- **Issues:** Final verdict that determines loop flow

### Information Isolation

The key to preventing collusion is strict information barriers:

```mermaid
flowchart LR
    subgraph Inputs[" "]
        REQ[Requirement]
        TESTS[Test Files]
        IMPL[Implementation]
    end

    subgraph Agents[" "]
        TW[Test Writer]
        CW[Code Writer]
        RV[Reviewer]
    end

    REQ -->|"✓"| TW
    REQ -.->|"✗"| CW
    REQ -->|"✓"| RV

    TESTS -.->|"✗"| TW
    TESTS -->|"✓ stripped"| CW
    TESTS -->|"✓"| RV

    IMPL -.->|"✗"| TW
    IMPL -.->|"✗"| CW
    IMPL -->|"✓"| RV
```

- **Test Writer** derives tests from requirements, never sees implementation
- **Code Writer** derives logic from test behavior, never sees requirements or comments
- **Reviewer** sees everything, filters feedback to prevent information leakage

---

## Philosophy

**Why adversarial?** Single-agent coding tends to "cheat" by writing tests that match the implementation rather than the spec. Three agents with different goals keep each other honest.

**Why isolation?** If the Code Writer sees the requirement, it might implement shortcuts that pass tests but miss intent. By only seeing tests, it must implement *behavior*, not just keywords.

**Why mutation testing?** Passing tests prove nothing if the tests themselves are weak. Mutation testing catches test suites that would pass broken code.

---

## Repository Structure

```
bon-cop-bad-cop/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── agents/                   # Agent definitions
│   ├── test-writer.md
│   ├── code-writer.md
│   └── reviewer.md
├── commands/                 # Slash commands
│   ├── tdd-loop.md
│   ├── tdd-status.md
│   ├── cancel-tdd.md
│   └── help.md
├── examples/                 # Example requirements
│   └── parse_duration_requirement.md
└── README.md
```

---

## Features

- **Information Isolation** - Each agent only sees what they should
- **Mutation Testing** - Ensures tests actually catch bugs
- **Cheating Detection** - Identifies hardcoded/lookup table implementations
- **Flakiness Detection** - Runs tests multiple times
- **State Persistence** - Loop state saved in `.tdd-working/state.json`
- **Requirement Grounding** - Original requirement re-injected every iteration to prevent drift
- **Trail Log** - Detailed audit log in `.tdd-loop.log` for debugging and verification
- **Context Management** - Optimized for long-running loops (up to 15 iterations) without exhausting context window

## Built-in Capabilities

The following capabilities are embedded directly in the agents and commands (no external dependencies):

### Cheating Detection (in Reviewer)
Analyzes implementation code for patterns indicating gaming rather than genuine logic:
- Hardcoded returns matching test expectations
- Lookup tables with test inputs as keys
- Test environment detection (`if 'pytest' in sys.modules`)
- Excessive conditional chains

### Flaky Test Detection (in Reviewer)
Runs test suite 3 times and compares results. Any test with inconsistent outcomes is flagged as flaky and must be fixed before proceeding.

### Comment Stripping (in Code Writer agent)
The Code Writer strips comments and docstrings from test files before implementing. Supports Python, JavaScript/TypeScript, Rust, Go, Java, and C/C++. This ensures Code Writer derives intent from test *behavior*, not explanatory comments.

### Requirement Alignment Check (in Reviewer)
Every iteration, the Reviewer verifies that tests still align with the original requirement. If tests have drifted beyond scope, the loop corrects back to the original requirement.

### Context Management (in all agents and orchestrator)
The plugin is designed for long-running loops without exhausting the context window:
- **Minimal agent responses** - Agents write verbose output to `.tdd-loop.log` and return only brief confirmations
- **History truncation** - Only the 3 most recent iterations are kept in `.tdd-state.json`; older iterations are archived to the log file
- **Log as primary record** - The `.tdd-loop.log` file contains complete history, mutation survivors, and detailed analysis

## Requirements

**For mutation testing (optional but recommended):**

Python:
```bash
pip install pytest mutmut
```

JavaScript:
```bash
npm install -D jest @stryker-mutator/core
```

Rust:
```bash
cargo install cargo-mutants
```

## Troubleshooting

### "Unknown slash command: tdd-loop"

Make sure the plugin is loaded. Either:
- Restart Claude Code with `claude --plugin-dir /path/to/bon-cop-bad-cop`
- Or add `pluginDirs` to your settings.json (see Installation above)

### Loop stops unexpectedly

If the loop stops before reaching ALL_PASS or max iterations:
1. Check `.tdd-state.json` - verify `"active": true` and check `lastVerdict`
2. Check `.tdd-loop.log` for error messages or the last recorded action
3. Run `/bon-cop-bad-cop:tdd-status` to see current state
4. The loop should continue automatically after each verdict unless ALL_PASS or max iterations reached
5. If it stops mid-loop, try running `/bon-cop-bad-cop:tdd-loop` again - it will detect the active state

### Tests not running / Mutation testing skipped

Install the required tools for your language (see Requirements above).

## Contributing

This is a community-built plugin. Contributions welcome!

## License

MIT
