# Bon Cop Bad Cop - Quick Start Guide

## Installation (One-Time Setup)

```bash
# 1. Start Claude Code
claude

# 2. Add this repo as a marketplace
/plugin marketplace add /path/to/bon-cop-bad-cop

# 3. Install the plugin
/plugin install bon-cop-bad-cop@bon-cop-bad-cop-marketplace
```

Done! The plugin is now globally available.

## Optional: Install Mutation Testing Tools

```bash
# Python
pip install pytest mutmut

# JavaScript (if needed)
npm install -D jest @stryker-mutator/core
```

## Usage

### Run a TDD Loop
```
/bon-cop-bad-cop:tdd-loop "Write a function add(a, b) that returns the sum of a and b"
```

### Check Progress
```
/bon-cop-bad-cop:tdd-status
```

### Cancel Loop
```
/bon-cop-bad-cop:cancel-tdd
```

## What Happens

1. **Test Writer Agent** creates comprehensive tests
2. **Code Writer Agent** implements code (sees only tests, not the requirement!)
3. **Reviewer Agent** runs tests, checks for cheating, validates quality
4. Loop continues based on verdict until **ALL_PASS** or max iterations

## Example Session

```bash
$ claude

> /bon-cop-bad-cop:tdd-loop "Write function fibonacci(n)"

Bon Cop Bad Cop - Adversarial TDD Loop
Loop initialized
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requirement: Write function fibonacci(n)
Max Iterations: 15
Mutation Threshold: 80%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Test Writer agent creates tests...]
[Code Writer agent implements...]
[Reviewer agent validates...]

ALL PASS - TDD Loop Complete!
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `/bon-cop-bad-cop:tdd-loop "requirement" [options]` | Start new TDD loop |
| `/bon-cop-bad-cop:tdd-status` | Check current loop status |
| `/bon-cop-bad-cop:cancel-tdd` | Cancel active loop |

### Options for tdd-loop

- `--max-iterations N` - Maximum iterations (default: 15)
- `--mutation-threshold 0.85` - Required mutation score (default: 0.8)
- `--test-scope unit|integration|both` - Test scope (default: unit)
- `--language python|javascript|rust` - Force language (default: auto-detect)

## Troubleshooting

**"Unknown slash command"**
- Run `/plugin list` to check if installed
- If not, follow Installation steps above

**Loop doesn't continue**
- Check `.tdd-state.json` has `"active": true`
- Check all agent files exist in `plugins/bon-cop-bad-cop/agents/`

**Need more help?**
- Check `README.md` for full documentation

## Repository Structure

```
bon-cop-bad-cop/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── plugins/
│   └── bon-cop-bad-cop/      # The plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── commands/
│       └── tools/
├── README.md
└── QUICKSTART.md
```
