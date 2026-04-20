#!/usr/bin/env python3
"""Check that tests using render_menu or render_confirmation follow the mocking pattern."""

import ast
import sys
import re
from pathlib import Path


def analyze_test_file(filepath: Path) -> tuple[bool, list[str]]:
    """Analyze a test file for mocking pattern issues.
    
    Returns:
        tuple of (has_issues, list of issue descriptions)
    """
    issues = []
    
    try:
        with open(filepath, "r") as f:
            source = f.read()
    except Exception as e:
        return False, [f"Could not read file: {e}"]
    
    # Parse the file to find actual method calls
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False, [f"File {filepath.name} has syntax errors"]
    
    # Find all render_menu/render_confirmation calls
    render_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ('render_menu', 'render_confirmation'):
                    # Get the line number
                    line_no = node.lineno
                    render_calls.append(line_no)
    
    if not render_calls:
        return False, []
    
    # Check if any of these calls are inside a patch('...newwin', ...) context
    # by looking for matching with statements
    
    lines = source.split("\n")
    
    for call_line in render_calls:
        # Look at the context around this call (up to 30 lines before and after)
        start = max(0, call_line - 30)
        end = min(len(lines), call_line + 5)
        context_lines = lines[start:end]
        context_text = "\n".join(context_lines)
        
        # Check if there's a patch('...newwin', ...) in the context
        # Accept both 'ui_manager.curses.newwin' and 'curses.newwin' patterns
        has_newwin_patch = bool(re.search(
            r"patch\s*\(\s*['\"]ui_manager.*?newwin.*?return_value",
            context_text
        ) or re.search(
            r"patch\s*\(\s*['\"]curses.*?newwin.*?return_value",
            context_text
        ))
        
        if not has_newwin_patch:
            # This call is not inside a newwin patch context
            # Check if it's inside a different patch context (e.g., patch.object on UIManager)
            has_other_patch = bool(re.search(r"patch\s*\(\s*\w+\s*\.\s*UIManager\s*\.\s*render_menu", context_text) or
                                   re.search(r"patch\s*\(\s*\w+\s*\.\s*UIManager\s*\.\s*render_confirmation", context_text))
            
            if not has_other_patch:
                issues.append(
                    f"Line {call_line}: render_menu/render_confirmation call on line {call_line} "
                    f"is not inside patch('ui_manager.curses.newwin', ...) context. "
                    f"Verify this test drives the render method or uses an appropriate mocking pattern."
                )
    
    return len(issues) > 0, issues


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: mocking_pattern_checker <directory>")
        sys.exit(1)
    
    test_dir = Path(sys.argv[1])
    
    if not test_dir.is_dir():
        print(f"Error: {test_dir} is not a directory")
        sys.exit(1)
    
    test_files = list(test_dir.glob("test_*.py"))
    test_files.extend(test_dir.glob("test_*_test.py"))
    
    if not test_files:
        print(f"No test files found in {test_dir}")
        sys.exit(0)
    
    all_has_issues = False
    all_issues = []
    
    for test_file in test_files:
        has_issues, issues = analyze_test_file(test_file)
        if has_issues:
            all_has_issues = True
            for issue in issues:
                all_issues.append((test_file.name, issue))
    
    if all_has_issues:
        print("\n⚠️  Mocking pattern issues found:\n")
        for filename, issue in all_issues:
            print(f"  [{filename}] {issue}")
        sys.exit(1)
    else:
        print("✅ All test files pass mocking pattern checks")
        sys.exit(0)


if __name__ == "__main__":
    main()
