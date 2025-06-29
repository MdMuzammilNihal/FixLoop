#!/usr/bin/env python
# Script to fix the final critical error in openfix_pro.py

import re

def fix_response_data_issue(file_path):
    """Fix the undefined response_data variable issue in a more targeted way."""
    print(f"Fixing remaining response_data issue in {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the location of the specific undefined response_data variable
    # Looking for the exact location around line 3239
    pattern = r'(def [^}]+?3239:40.*?response_data)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        # More explicit approach - find by surrounding context
        fix_location = content.find('        # Check if the response has a response key')
        if fix_location != -1:
            # Insert our fix before the problem area
            insertion_point = content.rfind('\n', 0, fix_location) + 1
            fixed_content = (
                content[:insertion_point] + 
                "        # Initialize response_data to avoid undefined variable issue\n" +
                "        response_data = {}\n" +
                content[insertion_point:]
            )
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
                
            print("Fixed response_data issue")
            return
    
    print("Could not find the exact position to fix response_data. Manual intervention needed.")

if __name__ == "__main__":
    fix_response_data_issue("openfix_pro.py") 