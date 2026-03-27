#!/usr/bin/env python3
"""
Direct runner for the QQQ Advanced Simulator
Run this file: python3 RUN_ME.py
"""

import os
import sys

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'src')

print("=" * 70)
print("Starting QQQ Advanced Simulator...")
print("=" * 70)

# Run the main program
from main_fixed import main

if __name__ == "__main__":
    main()

