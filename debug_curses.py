#!/usr/bin/env python3
"""
Debug script for llama-server-wrapper curses UI issue.

This script uses pexpect to run the wrapper and capture:
1. stdout/stderr output
2. Terminal state
3. Key presses
4. Screen capture

Run with: python3 debug_curses.py
"""

import pexpect
import sys
import os
import time
import re

def debug_wrapper():
    """Debug the wrapper using pexpect."""
    
    # Create a child process
    child = pexpect.spawn(
        "./llama-server-wrapper",
        args=["--install-llama"],
        encoding="utf-8",
        timeout=60
    )
    
    print("="*80)
    print("LAUNCHED llama-server-wrapper --install-llama")
    print("="*80)
    
    # Wait for initial output
    time.sleep(2)
    
    # Print buffer
    print("\n" + "="*80)
    print("OUTPUT BUFFER:")
    print(repr(child.before))
    print("="*80)
    
    # Check if process is still running
    if child.isalive():
        print("\nProcess is still running...")
        print("Waiting for process to complete...")
        
        # Wait for process to complete
        try:
            child.expect(pexpect.EOF, timeout=10)
        except pexpect.TIMEOUT:
            print("Process timed out, sending EOF")
            child.send_eof()
            child.expect(pexpect.EOF, timeout=5)
    
    print("\n" + "="*80)
    print("FINAL OUTPUT:")
    print(repr(child.after))
    print("="*80)
    
    # Print stdout
    print("\n" + "="*80)
    print("STDOUT:")
    print(child.stdout)
    print("="*80)
    
    # Print stderr  
    print("\n" + "="*80)
    print("STDERR:")
    print(child.stderr)
    print("="*80)

if __name__ == "__main__":
    try:
        debug_wrapper()
    except pexpect.ExceptionPexpect as e:
        print(f"Pexpect exception: {e}")
    except Exception as e:
        print(f"Exception: {e}")
