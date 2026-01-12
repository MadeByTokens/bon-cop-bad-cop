# Requirement: Duration Parser

Write a function `parse_duration(s)` that parses human-readable duration strings and returns the total number of seconds.

## Supported Units

| Unit | Symbol | Seconds |
|------|--------|---------|
| Days | d | 86400 |
| Hours | h | 3600 |
| Minutes | m | 60 |
| Seconds | s | 1 |

## Rules

1. Components can appear in any order: `"30m2h"` is valid (= 2h30m = 9000 seconds)
2. Components are optional: `"2h"` is valid (= 7200 seconds)
3. Each unit can only appear once: `"1h2h"` is invalid
4. Numbers must be non-negative integers: `"-5m"` and `"2.5h"` are invalid
5. Empty string returns 0
6. Invalid input returns `None`

## Examples

| Input | Output | Notes |
|-------|--------|-------|
| `"2h30m"` | `9000` | 2 hours + 30 minutes |
| `"1d"` | `86400` | 1 day |
| `"90s"` | `90` | 90 seconds |
| `"1d12h30m45s"` | `131445` | All components |
| `"30m2h"` | `9000` | Order doesn't matter |
| `""` | `0` | Empty string |
| `"abc"` | `None` | Invalid format |
| `"1h2h"` | `None` | Duplicate unit |
| `"-5m"` | `None` | Negative not allowed |
| `"2.5h"` | `None` | Decimals not allowed |
| `"5"` | `None` | No unit specified |
