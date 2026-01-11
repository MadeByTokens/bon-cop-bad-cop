---
name: strip-comments
description: Remove comments and docstrings from source code, preserving string literals
allowed-tools: Read, Write
---

# Strip Comments

Remove all comments and documentation from source code while preserving executable code and string literals.

## Step 1: Identify Language

Determine the language from file extension:

| Extension | Language |
|-----------|----------|
| .py, .pyi | Python |
| .js, .jsx, .mjs | JavaScript |
| .ts, .tsx | TypeScript |
| .java | Java |
| .c, .h | C |
| .cpp, .hpp, .cc | C++ |
| .rs | Rust |
| .go | Go |
| .rb | Ruby |
| .php | PHP |
| .html, .htm | HTML |
| .css, .scss | CSS |

## Step 2: Remove Comments by Language

### Python
```
Remove:
- # line comments
- """ or ''' docstrings (at module, class, function level)
- Inline # comments after code

Keep:
- '#' inside strings: print("use # for comments")
- Strings that look like docstrings but are assigned: x = """text"""
```

### JavaScript / TypeScript
```
Remove:
- // line comments
- /* block comments */
- /** JSDoc comments */

Keep:
- '//' inside strings: const url = "http://example.com"
- Regex literals: /\/\// (looks like comment but isn't)
- Template literals: `text // not comment`
```

### Java
```
Remove:
- // line comments
- /* block comments */
- /** Javadoc */

Keep:
- Comments inside string literals
```

### C / C++
```
Remove:
- // line comments (C99+, always in C++)
- /* block comments */

Keep:
- #include, #define, #ifdef (preprocessor directives)
- Comments in string literals
```

### Rust
```
Remove:
- // line comments
- /* block comments */
- /// and //! doc comments
- /** and /*! doc comments

Keep:
- Comments in string literals and raw strings r#""#
```

### Go
```
Remove:
- // line comments
- /* block comments */

Keep:
- Comments in string literals and raw strings ``
```

### HTML
```
Remove:
- <!-- HTML comments -->

Keep:
- Comments inside <script> or <style> (handle separately)
- Text content that looks like comments
```

### CSS
```
Remove:
- /* block comments */

Keep:
- Comments inside url() if any
```

## Step 3: Handle Edge Cases

### Strings containing comment characters
NEVER remove content inside string literals:
```python
# WRONG: Would break this
s = "Use # for comments"  # This comment should go, string stays

# RIGHT: Only remove actual comment
s = "Use # for comments"
```

### Nested comments (if language supports)
Remove entire nested structure:
```rust
/* outer /* inner */ still outer */
```

### Continued lines
Handle line continuations:
```python
x = 1 + \
    2  # comment here
```

### Regex literals (JavaScript)
```javascript
// This is a comment - REMOVE
const re = /\/\//;  // regex, not comment - KEEP
```

## Step 4: Output

Return the cleaned source code with:
- All comments removed
- Blank lines preserved (or collapsed to single blank)
- Indentation preserved
- String literals intact
