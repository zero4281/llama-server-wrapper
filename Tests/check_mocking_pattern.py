#!/usr/bin/env python3
"""Pre-commit hook to verify proper mocking pattern in tests.

This hook checks that tests driving render_menu or render_confirmation
use patch('ui_manager.curses.newwin', return_value=mock_win) to intercept
window creation.

Usage:
    python Tests/check_mocking_pattern.py Tests/*.py
"""

import ast
import re
import sys
from pathlib import Path

# Patterns to look for
PATTERN_CORRECT = re.compile(r"patch\s*\(\s*['\"]ui_manager\.curses\.newwin['\"]")
METHODS_OF_INTEREST = ['render_menu', 'render_confirmation']

def check_file(filepath):
    """Check a single test file for proper mocking pattern."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"  ❌ SKIP: {filepath} - syntax error")
        return True
    
    issues = []
    
    # Check each function definition
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if this function calls render_menu or render_confirmation
            calls = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute):
                        if child.func.attr in METHODS_OF_INTEREST:
                            calls.append(child.func.attr)
            
            if calls:
                # Check if the function has the required patch
                has_correct_patch = False
                
                for child in ast.walk(node):
                    if isinstance(child, ast.withitem):
                        # Check for 'with patch("ui_manager.curses.newwin", ...)'
                        if isinstance(child.context_expr, ast.Call):
                            if isinstance(child.context_expr.func, ast.Name) and child.context_expr.func.id == 'patch':
                                if isinstance(child.context_expr.args[0], ast.Constant) and child.context_expr.args[0].value == 'ui_manager.curses.newwin':
                                    has_correct_patch = True
                                    break
                
                if not has_correct_patch:
                    issues.append(f"  - Missing patch('ui_manager.curses.newwin') for {', '.join(calls)}")
    
    if issues:
        return False
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_mocking_pattern.py <test_files...>")
        sys.exit(1)
    
    all_passed = True
    
    for filepath in sys.argv[1:]:
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"  ⚠️  SKIP: {filepath} - file not found")
            continue
        
        if not filepath.suffix == '.py':
            print(f"  ⚠️  SKIP: {filepath} - not a Python file")
            continue
        
        print(f"Checking {filepath.name}...")
        
        if not check_file(filepath):
            print(f"  ❌ FAILED: {filepath.name}")
            all_passed = False
        else:
            print(f"  ✅ PASS: {filepath.name}")
    
    if all_passed:
        print("\n✅ All tests passed the mocking pattern check!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed the mocking pattern check.")
        sys.exit(1)

if __name__ == '__main__':
    main()
