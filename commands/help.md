---
description: Display help information for Bon Cop Bad Cop plugin
allowed-tools: []
---

# /help Command

When the user runs `/help`, display the following information:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 **Bon Cop Bad Cop - Adversarial TDD Plugin**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Three-agent adversarial TDD loop where agents keep each other honest.

**Commands:**

  /bon-cop-bad-cop:tdd-loop "requirement" [options]
  /bon-cop-bad-cop:tdd-loop --requirement-file <path> [options]
  /bon-cop-bad-cop:tdd-loop "extra notes" --requirement-file <path> [options]
      Start a new TDD loop with the given requirement.
      
      Options:
        --requirement-file PATH  Load requirement from markdown file
                                 (can combine with inline text for notes)
        --max-iterations N       Max loop iterations (default: 15)
        --mutation-threshold X   Required mutation score 0.0-1.0 (default: 0.8)
        --test-scope SCOPE       unit | integration | both (default: unit)
        --language LANG          Override auto-detection (python, javascript,
                                 typescript, rust, go, java, ruby)

  /bon-cop-bad-cop:tdd-status
      Check the current TDD loop status and progress.

  /bon-cop-bad-cop:cancel-tdd
      Cancel the active TDD loop.

  /bon-cop-bad-cop:help
      Display this help message.

**Quick Start:**

  /bon-cop-bad-cop:tdd-loop "Write a function is_prime(n)"

**How It Works:**

  1. Test Writer (Bad Cop) → Creates comprehensive tests
  2. Code Writer (Suspect) → Implements code (sees only tests!)
  3. Reviewer (Good Cop)   → Validates and issues verdict

  Loop continues until ALL_PASS or max iterations reached.

**More Info:** See README.md for full documentation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
