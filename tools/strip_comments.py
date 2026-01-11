#!/usr/bin/env python3
"""
Strip comments and docstrings from test files.

This ensures Code Writer derives intent from test BEHAVIOR, not from
explanatory comments. This is a key anti-collusion measure.

Usage:
    python strip_comments.py <input_file> [output_file]
    
If output_file is omitted, prints to stdout.
"""

import ast
import sys
import re
from pathlib import Path


def strip_python_comments(source: str) -> str:
    """Remove comments and docstrings from Python source code."""
    
    # Remove docstrings using AST (more reliable)
    try:
        tree = ast.parse(source)
        
        # Find all docstring locations
        docstring_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    docstring_node = node.body[0]
                    for line in range(docstring_node.lineno, docstring_node.end_lineno + 1):
                        docstring_lines.add(line)
    except SyntaxError:
        # If we can't parse, fall back to regex
        docstring_lines = set()
    
    lines = source.split('\n')
    result_lines = []

    for i, line in enumerate(lines, 1):
        # Skip docstring lines identified by AST
        if i in docstring_lines:
            # Keep the line structure but remove content
            indent = len(line) - len(line.lstrip())
            result_lines.append(' ' * indent + 'pass  # docstring removed')
            continue
        
        # Remove inline comments (but preserve strings)
        new_line = remove_inline_comments(line)
        
        # Skip pure comment lines
        if new_line.strip().startswith('#'):
            continue
            
        result_lines.append(new_line)
    
    # Clean up multiple blank lines
    result = '\n'.join(result_lines)
    result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
    
    return result


def remove_inline_comments(line: str) -> str:
    """Remove comments from a line while preserving strings."""
    result = []
    in_string = False
    string_char = None
    i = 0
    
    while i < len(line):
        char = line[i]
        
        if in_string:
            result.append(char)
            if char == '\\' and i + 1 < len(line):
                result.append(line[i + 1])
                i += 2
                continue
            if char == string_char:
                in_string = False
            i += 1
        elif char in '"\'':
            # Check for triple quotes
            if line[i:i+3] in ('"""', "'''"):
                result.append(line[i:i+3])
                string_char = line[i:i+3]
                in_string = True
                i += 3
            else:
                result.append(char)
                string_char = char
                in_string = True
                i += 1
        elif char == '#':
            # Found a comment, stop here
            break
        else:
            result.append(char)
            i += 1
    
    return ''.join(result).rstrip()


def strip_javascript_comments(source: str) -> str:
    """Remove comments from JavaScript/TypeScript source code."""
    
    # Remove single-line comments (but not in strings)
    result = []
    lines = source.split('\n')
    
    in_multiline = False
    
    for line in lines:
        if in_multiline:
            if '*/' in line:
                line = line[line.index('*/') + 2:]
                in_multiline = False
            else:
                continue
        
        # Remove /* */ comments
        while '/*' in line:
            start = line.index('/*')
            if '*/' in line[start:]:
                end = line.index('*/', start) + 2
                line = line[:start] + line[end:]
            else:
                line = line[:start]
                in_multiline = True
                break
        
        # Remove // comments (naive - doesn't handle strings perfectly)
        if '//' in line:
            # Simple heuristic: only remove if not inside a string
            in_string = False
            string_char = None
            new_line = []
            i = 0
            while i < len(line):
                if in_string:
                    new_line.append(line[i])
                    if line[i] == '\\' and i + 1 < len(line):
                        new_line.append(line[i + 1])
                        i += 2
                        continue
                    if line[i] == string_char:
                        in_string = False
                    i += 1
                elif line[i] in '"\'`':
                    new_line.append(line[i])
                    string_char = line[i]
                    in_string = True
                    i += 1
                elif line[i:i+2] == '//':
                    break
                else:
                    new_line.append(line[i])
                    i += 1
            line = ''.join(new_line)
        
        result.append(line.rstrip())
    
    return '\n'.join(result)


def strip_comments(filepath: str) -> str:
    """Strip comments from a file based on its extension."""
    path = Path(filepath)
    content = path.read_text()
    
    if path.suffix in ('.py', '.pyi'):
        return strip_python_comments(content)
    elif path.suffix in ('.js', '.ts', '.jsx', '.tsx', '.mjs'):
        return strip_javascript_comments(content)
    else:
        # Unknown file type, return as-is with warning
        print(f"Warning: Unknown file type {path.suffix}, returning unchanged", 
              file=sys.stderr)
        return content


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = strip_comments(input_file)
    
    if output_file:
        Path(output_file).write_text(result)
    else:
        print(result)


if __name__ == '__main__':
    main()
