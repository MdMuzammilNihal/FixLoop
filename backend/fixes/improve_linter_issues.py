#!/usr/bin/env python
# Script to fix the remaining critical linter issues in openfix_pro.py

import re
import os

def fix_remaining_critical_issues(file_path):
    """Fix remaining critical linter issues in the specified file."""
    print(f"Fixing remaining critical issues in {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Fix the undefined 'response_data' variable
    response_data_fix = """        # Initialize response_data
        response_data = {}
        try:
            response_data = response.json()
        except Exception as e:
            print(f"[INFO] Error parsing response: {str(e)}")
"""
    # Find the location where response_data is first used without definition
    match = re.search(r'(?<=\n        )response_data =', content)
    if match:
        # Insert the definition before the first usage
        pos = match.start()
        content = content[:pos] + "# Initialize response_data\n        response_data = {}\n        " + content[pos:]
    
    # Fix 2: Fix the redefined startup_event function
    # Replace the redefined function with a different name
    content = content.replace(
        "async def startup_event():",
        "async def alternative_startup_event():",
        1  # Replace only the first occurrence after the original definition
    )
    
    # Fix 3: Remove unused variable 'e' assignments in except blocks
    content = re.sub(
        r'except Exception as e:\s+pass',
        'except Exception:\n            pass',
        content
    )
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Critical linter issues fixed.")

if __name__ == "__main__":
    fix_remaining_critical_issues("openfix_pro.py") 