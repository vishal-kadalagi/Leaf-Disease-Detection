#!/usr/bin/env python3
"""
Test script to verify ImportError handling
"""

print("Testing ImportError handling...")

try:
    import nonexistent_module
except ImportError as ie:
    print(f"ImportError caught: {ie}")
    print(f"Error type: {type(ie)}")
    if hasattr(ie, 'name'):
        print(f"Module name: {ie.name}")
    else:
        print("No 'name' attribute in ImportError")