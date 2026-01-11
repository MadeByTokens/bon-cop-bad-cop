#!/usr/bin/env python3
"""
Flaky Test Detection Utility

Runs test suite multiple times and identifies tests with inconsistent results.
Any flaky tests must be fixed before proceeding with mutation testing.

Usage:
    python detect_flaky.py [--runs N] [--framework FRAMEWORK] [test_path]
    
Options:
    --runs N          Number of times to run tests (default: 3)
    --framework FW    Test framework: pytest, jest, cargo (default: auto-detect)
    test_path         Path to tests (default: tests/)

Output:
    JSON with flaky test information, or "STABLE" if no flaky tests found.
"""

import argparse
import json
import subprocess
import sys
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class TestResult:
    name: str
    outcomes: list[str]  # "PASS", "FAIL", "ERROR", "SKIP"
    is_flaky: bool
    
    @property
    def summary(self) -> str:
        return ", ".join(self.outcomes)


@dataclass
class FlakyReport:
    total_tests: int
    flaky_tests: list[TestResult]
    stable_tests: int
    runs: int
    framework: str
    
    @property
    def is_stable(self) -> bool:
        return len(self.flaky_tests) == 0


def detect_framework(test_path: str) -> str:
    """Auto-detect test framework based on files present."""
    path = Path(test_path)
    
    # Check for pytest
    if list(path.glob("**/test_*.py")) or list(path.glob("**/*_test.py")):
        if Path("pytest.ini").exists() or Path("pyproject.toml").exists():
            return "pytest"
        return "pytest"
    
    # Check for Jest
    if list(path.glob("**/*.test.js")) or list(path.glob("**/*.test.ts")):
        return "jest"
    
    # Check for Cargo
    if Path("Cargo.toml").exists():
        return "cargo"
    
    # Default to pytest
    return "pytest"


def run_pytest(test_path: str) -> dict[str, str]:
    """Run pytest and return test results."""
    result = subprocess.run(
        ["pytest", test_path, "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    results = {}
    
    # Parse pytest output
    # Format: "test_file.py::test_name PASSED/FAILED/ERROR/SKIPPED"
    for line in output.split('\n'):
        match = re.match(r'(.+::.+)\s+(PASSED|FAILED|ERROR|SKIPPED)', line)
        if match:
            test_name = match.group(1)
            outcome = match.group(2)
            results[test_name] = outcome.replace("PASSED", "PASS").replace("SKIPPED", "SKIP")
    
    return results


def run_jest(test_path: str) -> dict[str, str]:
    """Run Jest and return test results."""
    result = subprocess.run(
        ["npx", "jest", test_path, "--json", "--testLocationInResults"],
        capture_output=True,
        text=True
    )
    
    results = {}
    try:
        data = json.loads(result.stdout)
        for test_result in data.get("testResults", []):
            for assertion in test_result.get("assertionResults", []):
                test_name = f"{test_result['name']}::{assertion['fullName']}"
                status = assertion["status"]
                results[test_name] = {
                    "passed": "PASS",
                    "failed": "FAIL",
                    "pending": "SKIP"
                }.get(status, "ERROR")
    except json.JSONDecodeError:
        # Fall back to parsing text output
        pass
    
    return results


def run_cargo(test_path: str) -> dict[str, str]:
    """Run Cargo test and return results."""
    result = subprocess.run(
        ["cargo", "test", "--", "--test-threads=1"],
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    results = {}
    
    # Parse cargo test output
    # Format: "test module::test_name ... ok/FAILED"
    for line in output.split('\n'):
        match = re.match(r'test\s+(\S+)\s+\.\.\.\s+(ok|FAILED|ignored)', line)
        if match:
            test_name = match.group(1)
            outcome = match.group(2)
            results[test_name] = {
                "ok": "PASS",
                "FAILED": "FAIL",
                "ignored": "SKIP"
            }.get(outcome, "ERROR")
    
    return results


def run_tests(framework: str, test_path: str) -> dict[str, str]:
    """Run tests using the specified framework."""
    runners = {
        "pytest": run_pytest,
        "jest": run_jest,
        "cargo": run_cargo
    }
    
    runner = runners.get(framework)
    if not runner:
        raise ValueError(f"Unknown framework: {framework}")
    
    return runner(test_path)


def detect_flaky_tests(
    test_path: str = "tests/",
    runs: int = 3,
    framework: Optional[str] = None
) -> FlakyReport:
    """
    Run tests multiple times and identify flaky tests.
    
    Args:
        test_path: Path to test directory
        runs: Number of times to run the test suite
        framework: Test framework (auto-detected if not specified)
    
    Returns:
        FlakyReport with results
    """
    if framework is None:
        framework = detect_framework(test_path)
    
    # Collect results from multiple runs
    all_results: list[dict[str, str]] = []
    
    print(f"Running {framework} tests {runs} times...", file=sys.stderr)
    
    for i in range(runs):
        print(f"  Run {i + 1}/{runs}...", file=sys.stderr)
        results = run_tests(framework, test_path)
        all_results.append(results)
    
    # Analyze results
    all_test_names = set()
    for results in all_results:
        all_test_names.update(results.keys())
    
    test_results: list[TestResult] = []
    flaky_tests: list[TestResult] = []
    
    for test_name in sorted(all_test_names):
        outcomes = [
            results.get(test_name, "MISSING")
            for results in all_results
        ]
        
        # A test is flaky if it has different outcomes across runs
        unique_outcomes = set(outcomes)
        is_flaky = len(unique_outcomes) > 1
        
        result = TestResult(
            name=test_name,
            outcomes=outcomes,
            is_flaky=is_flaky
        )
        test_results.append(result)
        
        if is_flaky:
            flaky_tests.append(result)
    
    return FlakyReport(
        total_tests=len(test_results),
        flaky_tests=flaky_tests,
        stable_tests=len(test_results) - len(flaky_tests),
        runs=runs,
        framework=framework
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test_path", nargs="?", default="tests/",
                        help="Path to tests")
    parser.add_argument("--runs", type=int, default=3,
                        help="Number of test runs")
    parser.add_argument("--framework", choices=["pytest", "jest", "cargo"],
                        help="Test framework (auto-detected if not specified)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    report = detect_flaky_tests(
        test_path=args.test_path,
        runs=args.runs,
        framework=args.framework
    )
    
    if args.json:
        output = {
            "stable": report.is_stable,
            "total_tests": report.total_tests,
            "stable_tests": report.stable_tests,
            "flaky_count": len(report.flaky_tests),
            "runs": report.runs,
            "framework": report.framework,
            "flaky_tests": [asdict(t) for t in report.flaky_tests]
        }
        print(json.dumps(output, indent=2))
    else:
        if report.is_stable:
            print("STABLE")
            print(f"All {report.total_tests} tests passed consistently across {report.runs} runs.")
        else:
            print("FLAKY TESTS DETECTED")
            print(f"\nFramework: {report.framework}")
            print(f"Runs: {report.runs}")
            print(f"Total tests: {report.total_tests}")
            print(f"Flaky tests: {len(report.flaky_tests)}")
            print(f"Stable tests: {report.stable_tests}")
            print("\nFlaky test details:")
            for test in report.flaky_tests:
                print(f"\n  {test.name}")
                print(f"    Results: {test.summary}")
            
            sys.exit(1)


if __name__ == "__main__":
    main()
