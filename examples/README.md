# Examples

This folder contains example requirements you can use to test the Bon Cop Bad Cop TDD loop.

## Usage

### Using a requirement file

```bash
/bon-cop-bad-cop:tdd-loop --requirement-file examples/parse_duration_requirement.md
```

### Adding extra notes

You can combine a requirement file with inline notes:

```bash
/bon-cop-bad-cop:tdd-loop "Focus on error handling first" --requirement-file examples/parse_duration_requirement.md
```

### With options

```bash
/bon-cop-bad-cop:tdd-loop --requirement-file examples/parse_duration_requirement.md --language python --max-iterations 10
```

## Monitoring Progress

Watch the trail log in real-time:

```bash
tail -f .tdd-loop.log
```

Check loop status:

```bash
/bon-cop-bad-cop:tdd-status
```

Cancel if needed:

```bash
/bon-cop-bad-cop:cancel-tdd
```

## Generated Files

After running, you'll find:

| File | Description |
|------|-------------|
| `.tdd-state.json` | Loop state (iteration, verdict, feedback, history) |
| `.tdd-loop.log` | Timestamped trail log of all actions |
| `test_*.py` | Generated test files (or equivalent for other languages) |
| `*.py` | Generated implementation files |

## Available Examples

| File | Description | Difficulty |
|------|-------------|------------|
| `parse_duration_requirement.md` | Parse duration strings like "2h30m" to seconds | Medium-Hard |

## Quick Test Commands

Simple inline requirements to try:

```bash
# Easy
/bon-cop-bad-cop:tdd-loop "Write a function add(a, b) that returns the sum of two numbers"

# Medium
/bon-cop-bad-cop:tdd-loop "Write a function is_palindrome(s) that returns True if the string is a palindrome (ignoring case and spaces)"

# Hard
/bon-cop-bad-cop:tdd-loop "Write a function eval_rpn(tokens) that evaluates a list of tokens in Reverse Polish Notation and returns the result. Support +, -, *, / operators with integer division."
```
