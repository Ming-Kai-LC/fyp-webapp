#!/usr/bin/env python
"""
Helper script to run makemigrations with proper input handling
"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create input file with responses for Django's prompts
# Response format: 1 (option 1), then empty line (accept timezone.now default) for each model
# We need to provide many responses since there are many models that need this
responses = []
for _ in range(50):  # More than enough responses
    responses.append("1")  # Option 1: Provide a one-off default
    responses.append("")   # Accept timezone.now default

input_text = "\n".join(responses)

# Run makemigrations with the input
process = subprocess.Popen(
    [sys.executable, 'manage.py', 'makemigrations'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace'
)

stdout, _ = process.communicate(input=input_text)
print(stdout)
print(f"\nExit code: {process.returncode}")
