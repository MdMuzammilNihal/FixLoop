#!/usr/bin/env python
# Script to fix the syntax error in openfix_pro.py

with open('openfix_pro.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the syntax error - properly separate closing triple quotes from code
fixed_content = content.replace(
    'except Exception as e:    print(f"[INFO] Visualization save operations: {str(e)}")"""        modified_code',
    'except Exception as e:\n        print(f"[INFO] Visualization save operations: {str(e)}")\n"""\n        modified_code'
)

with open('openfix_pro.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed the syntax error in openfix_pro.py") 