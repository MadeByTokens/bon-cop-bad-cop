#!/usr/bin/env python3
"""
Cheating Pattern Detector

Scans implementation code for patterns that indicate the Code Writer
is "cheating" rather than implementing genuine logic.

Patterns detected:
1. Hardcoded return values matching test expectations
2. Lookup tables with test inputs as keys
3. Conditional chains matching specific test cases
4. Test environment detection

Usage:
    python detect_cheating.py <impl_file> <test_file>
    
Output:
    JSON report of detected cheating patterns, or "CLEAN" if none found.
"""

import ast
import json
import sys
import re
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class CheatingPattern:
    pattern_type: str
    description: str
    file: str
    line: int
    code_snippet: str
    severity: str  # "high", "medium", "low"


def extract_test_values(test_file: str) -> dict:
    """Extract literal values used in test assertions."""
    content = Path(test_file).read_text()
    tree = ast.parse(content)
    
    test_values = {
        "inputs": set(),
        "outputs": set(),
        "comparisons": []
    }
    
    class TestValueExtractor(ast.NodeVisitor):
        def visit_Assert(self, node):
            # Look for assert statements with comparisons
            if isinstance(node.test, ast.Compare):
                self._extract_comparison(node.test)
            self.generic_visit(node)
        
        def visit_Call(self, node):
            # Look for assertEqual, assertEquals, etc.
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ('assertEqual', 'assertEquals', 'assertAlmostEqual'):
                    if len(node.args) >= 2:
                        for arg in node.args:
                            self._extract_value(arg)
            self.generic_visit(node)
        
        def _extract_comparison(self, node):
            if isinstance(node, ast.Compare):
                self._extract_value(node.left)
                for comp in node.comparators:
                    self._extract_value(comp)
        
        def _extract_value(self, node):
            if isinstance(node, ast.Constant):
                test_values["outputs"].add(repr(node.value))
            elif isinstance(node, ast.Tuple):
                for elt in node.elts:
                    self._extract_value(elt)
            elif isinstance(node, ast.Call):
                # Extract function call arguments
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        test_values["inputs"].add(repr(arg.value))
    
    TestValueExtractor().visit(tree)
    return test_values


def detect_hardcoded_returns(impl_file: str, test_values: dict) -> list[CheatingPattern]:
    """Detect if-conditions that return specific test values."""
    patterns = []
    content = Path(impl_file).read_text()
    lines = content.split('\n')
    tree = ast.parse(content)
    
    class HardcodeDetector(ast.NodeVisitor):
        def visit_If(self, node):
            # Check if the condition involves specific values
            condition_str = ast.unparse(node.test)
            
            # Check if return value matches test expectations
            for stmt in node.body:
                if isinstance(stmt, ast.Return) and stmt.value:
                    return_val = ast.unparse(stmt.value)
                    
                    # Check for direct matches with test values
                    if return_val in test_values["outputs"]:
                        # Check if condition uses specific input values
                        if any(inp in condition_str for inp in test_values["inputs"]):
                            patterns.append(CheatingPattern(
                                pattern_type="hardcoded_return",
                                description=f"Returns {return_val} when condition matches test input",
                                file=impl_file,
                                line=node.lineno,
                                code_snippet=lines[node.lineno - 1].strip(),
                                severity="high"
                            ))
            
            self.generic_visit(node)
    
    HardcodeDetector().visit(tree)
    return patterns


def detect_lookup_tables(impl_file: str, test_values: dict) -> list[CheatingPattern]:
    """Detect dictionary/map definitions with test inputs as keys."""
    patterns = []
    content = Path(impl_file).read_text()
    lines = content.split('\n')
    tree = ast.parse(content)
    
    class LookupDetector(ast.NodeVisitor):
        def visit_Dict(self, node):
            # Check if dictionary keys match test inputs
            key_matches = 0
            for key in node.keys:
                if key:
                    key_str = ast.unparse(key)
                    if key_str in test_values["inputs"]:
                        key_matches += 1
            
            # If multiple keys match test inputs, likely a lookup table
            if key_matches >= 2:
                patterns.append(CheatingPattern(
                    pattern_type="lookup_table",
                    description=f"Dictionary with {key_matches} keys matching test inputs",
                    file=impl_file,
                    line=node.lineno,
                    code_snippet=lines[node.lineno - 1].strip()[:80],
                    severity="high"
                ))
            
            self.generic_visit(node)
    
    LookupDetector().visit(tree)
    return patterns


def detect_test_environment_checks(impl_file: str) -> list[CheatingPattern]:
    """Detect code that checks if running in test environment."""
    patterns = []
    content = Path(impl_file).read_text()
    lines = content.split('\n')
    
    # Common test detection patterns
    test_detection_patterns = [
        (r'pytest.*in.*sys\.modules', "pytest module detection"),
        (r'unittest.*in.*sys\.modules', "unittest module detection"),
        (r'__name__.*==.*[\'"]__main__[\'"].*test', "main check with test"),
        (r'os\.environ\.get\([\'"]TEST', "TEST environment variable"),
        (r'os\.environ\.get\([\'"]CI[\'"]', "CI environment variable"),
        (r'TESTING.*=.*True', "TESTING flag"),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, description in test_detection_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                patterns.append(CheatingPattern(
                    pattern_type="test_detection",
                    description=description,
                    file=impl_file,
                    line=i,
                    code_snippet=line.strip(),
                    severity="high"
                ))
    
    return patterns


def detect_excessive_conditionals(impl_file: str) -> list[CheatingPattern]:
    """Detect functions with suspiciously many if-elif chains."""
    patterns = []
    content = Path(impl_file).read_text()
    tree = ast.parse(content)
    
    class ConditionalCounter(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            # Count if statements in function
            if_count = sum(1 for _ in ast.walk(node) if isinstance(_, ast.If))
            
            # Heuristic: more than 5 if statements in a small function is suspicious
            line_count = node.end_lineno - node.lineno
            if if_count > 5 and if_count > line_count / 3:
                patterns.append(CheatingPattern(
                    pattern_type="excessive_conditionals",
                    description=f"Function '{node.name}' has {if_count} conditionals in {line_count} lines",
                    file=impl_file,
                    line=node.lineno,
                    code_snippet=f"def {node.name}(...):",
                    severity="medium"
                ))
            
            self.generic_visit(node)
    
    ConditionalCounter().visit(tree)
    return patterns


def detect_cheating(impl_file: str, test_file: str) -> list[CheatingPattern]:
    """Run all cheating detection checks."""
    all_patterns = []
    
    # Extract test values for comparison
    test_values = extract_test_values(test_file)
    
    # Run all detectors
    all_patterns.extend(detect_hardcoded_returns(impl_file, test_values))
    all_patterns.extend(detect_lookup_tables(impl_file, test_values))
    all_patterns.extend(detect_test_environment_checks(impl_file))
    all_patterns.extend(detect_excessive_conditionals(impl_file))
    
    return all_patterns


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    impl_file = sys.argv[1]
    test_file = sys.argv[2]
    json_output = "--json" in sys.argv
    
    patterns = detect_cheating(impl_file, test_file)
    
    if json_output:
        output = {
            "clean": len(patterns) == 0,
            "patterns": [asdict(p) for p in patterns],
            "high_severity": sum(1 for p in patterns if p.severity == "high"),
            "medium_severity": sum(1 for p in patterns if p.severity == "medium"),
            "low_severity": sum(1 for p in patterns if p.severity == "low")
        }
        print(json.dumps(output, indent=2))
    else:
        if not patterns:
            print("CLEAN")
            print("No cheating patterns detected.")
        else:
            print("CHEATING PATTERNS DETECTED")
            print(f"\nTotal patterns found: {len(patterns)}")
            
            high = [p for p in patterns if p.severity == "high"]
            medium = [p for p in patterns if p.severity == "medium"]
            
            if high:
                print(f"\n🚨 HIGH SEVERITY ({len(high)}):")
                for p in high:
                    print(f"\n  [{p.pattern_type}] Line {p.line}")
                    print(f"  {p.description}")
                    print(f"  Code: {p.code_snippet}")
            
            if medium:
                print(f"\n⚠️ MEDIUM SEVERITY ({len(medium)}):")
                for p in medium:
                    print(f"\n  [{p.pattern_type}] Line {p.line}")
                    print(f"  {p.description}")
            
            sys.exit(1)


if __name__ == "__main__":
    main()
