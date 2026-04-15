#!/usr/bin/env python3
"""
Test script for UIManager.

This script tests the UIManager by simulating what happens when the wrapper runs.
"""

import sys
import time

# Add current directory to path
sys.path.insert(0, str(__import__('pathlib').Path.cwd()))

from ui_manager import UIManager

def test_ui_manager():
    """Test the UIManager."""
    print("="*80)
    print("TESTING UI MANAGER")
    print("="*80)
    
    try:
        # Create UIManager
        ui = UIManager("Test")
        print("UIManager created successfully")
        
        # Test print_message
        ui.print_message("Hello from UIManager!")
        time.sleep(0.5)
        
        # Test render_menu
        options = [
            {'label': 'Option 1', 'description': 'First option'},
            {'label': 'Option 2', 'description': 'Second option'},
            {'label': 'Option 3', 'description': 'Third option'},
        ]
        print("\nTesting render_menu...")
        
        # We can't actually test the menu without user input, but we can test that it doesn't crash
        # Just refresh the screen to force a redraw
        ui.refresh()
        print("Screen refreshed")
        
        # Test render_confirmation
        print("\nTesting render_confirmation...")
        confirmed = ui.render_confirmation("Test confirmation message")
        print(f"Confirmed: {confirmed}")
        
        # Test render_progress_bar
        print("\nTesting render_progress_bar...")
        ui.render_progress_bar("test.zip", 100, 1000)
        
        print("\n" + "="*80)
        print("ALL TESTS PASSED")
        print("="*80)
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            ui._close()
        except:
            pass
    
    return True

if __name__ == "__main__":
    test_ui_manager()
