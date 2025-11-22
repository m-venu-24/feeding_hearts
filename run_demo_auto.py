#!/usr/bin/env python3
"""
Automated AI Error Prediction System Demo
Runs without user interaction
"""

import sys
import os

# Patch input to auto-continue
original_input = input
def auto_input(prompt=""):
    print(prompt)
    return ""

# Replace input globally
__builtins__.input = auto_input

# Import and run the demo
from demo_ai_prediction_system import AIErrorPredictionDemo

if __name__ == "__main__":
    demo = AIErrorPredictionDemo()
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted")
        sys.exit(0)
