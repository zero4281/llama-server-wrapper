#!/usr/bin/env python3
"""
Tests/__init__.py — Unified test entry point for UIManager tests.

Run with: pytest Tests/ -v
Or: python3 Tests/__init__.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

def run_tests():
    """Run all test modules."""
    import importlib
    import os
    
    tests_dir = Path(__file__).parent
    test_files = sorted(tests_dir.glob('test_*.py'))
    
    if not test_files:
        print("No test files found in Tests directory.")
        return 1
    
    print(f"Found {len(test_files)} test file(s):")
    for f in test_files:
        print(f"  - {f.name}")
    
    all_passed = True
    
    for test_file in test_files:
        # Import the module
        module_name = f"Tests.{test_file.stem}"
        try:
            module = importlib.import_module(module_name)
            
            # Run tests if there's a run_tests function
            if hasattr(module, 'run_tests') and callable(module.run_tests):
                print(f"\nRunning {test_file.stem}...")
                print("-" * 40)
                try:
                    result = module.run_tests()
                    if result is False:
                        all_passed = False
                except Exception as e:
                    print(f"ERROR in {test_file.stem}: {e}")
                    import traceback
                    traceback.print_exc()
                    all_passed = False
            elif hasattr(module, 'run_all_tests') and callable(module.run_all_tests):
                print(f"\nRunning {test_file.stem}...")
                print("-" * 40)
                try:
                    module.run_all_tests()
                except Exception as e:
                    print(f"ERROR in {test_file.stem}: {e}")
                    import traceback
                    traceback.print_exc()
                    all_passed = False
            else:
                # Pytest-compatible
                print(f"\nRunning {test_file.stem} (pytest)...")
                print("-" * 40)
                try:
                    if __name__ == '__main__':
                        import pytest
                        pytest.main([str(test_file), '-v'])
                except Exception as e:
                    print(f"ERROR in {test_file.stem}: {e}")
                    import traceback
                    traceback.print_exc()
                    all_passed = False
                    
        except Exception as e:
            print(f"ERROR importing {test_file.stem}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
