#!/usr/bin/env python
# Script to fix the function redefinition error in openfix_pro.py

import re

def fix_function_redefinition(file_path):
    """Fix the function redefinition error."""
    print(f"Fixing function redefinition in {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the second occurrence of the startup_event function
    # Count how many times the function appears
    startup_count = content.count("async def startup_event():")
    
    if startup_count > 1:
        # Find the position of the first occurrence
        first_pos = content.find("async def startup_event():")
        # Find the position of the second occurrence
        second_pos = content.find("async def startup_event():", first_pos + 1)
        
        if second_pos != -1:
            # Replace the second occurrence with an alternative name
            content = (
                content[:second_pos] + 
                "async def alternative_startup_event():" + 
                content[second_pos + len("async def startup_event():"):]
            )
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print("Fixed function redefinition")
            return
        
    print("No function redefinition found or couldn't fix it.")

if __name__ == "__main__":
    fix_function_redefinition("openfix_pro.py") 