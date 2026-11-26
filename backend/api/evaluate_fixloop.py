import requests
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate
import os

API_URL = "http://localhost:8000/api"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80 + "\n")

def evaluate_response(response, expected_keys=None, success_criteria=None):
    """Evaluate API response and return score and feedback"""
    score = 0
    feedback = []
    
    # Check for HTTP success
    if response.status_code == 200:
        score += 1
        feedback.append("[OK] API call successful")
    else:
        feedback.append(f"[FAIL] API call failed with status {response.status_code}")
        return score, feedback
    
    # Parse response
    try:
        data = response.json()
        feedback.append("[OK] Response is valid JSON")
        score += 1
    except ValueError:
        feedback.append("[FAIL] Response is not valid JSON")
        return score, feedback
    
    # Check for expected keys
    if expected_keys:
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            feedback.append(f"[FAIL] Missing expected keys: {missing_keys}")
        else:
            feedback.append("[OK] All expected keys present")
            score += 1
    
    # Check success criteria if provided
    if success_criteria and callable(success_criteria):
        success, reason = success_criteria(data)
        if success:
            feedback.append(f"[OK] {reason}")
            score += 1
        else:
            feedback.append(f"[FAIL] {reason}")
    
    return score, feedback

def check_code_analysis():
    """Test code analysis functionality"""
    print_section("Testing Code Analysis")
    
    # Test 1: Basic analysis
    code = """
def calculate_factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
    """
    
    print("Test 1: Basic code analysis")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": code, "language": "python", "action": "analyze"}
    )
    
    score, feedback = evaluate_response(
        response, 
        expected_keys=["original_code", "errors", "warnings", "suggestions", "processing_time"],
        success_criteria=lambda data: (
            len(data.get("warnings", [])) > 0 or len(data.get("suggestions", [])) > 0,
            "Provided analysis with warnings or suggestions"
        )
    )
    
    for item in feedback:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n  Analysis Results:")
        if "errors" in data and data["errors"]:
            print(f"  - Errors: {len(data['errors'])}")
        if "warnings" in data and data["warnings"]:
            print(f"  - Warnings: {len(data['warnings'])}")
        if "suggestions" in data and data["suggestions"]:
            print(f"  - Suggestions: {len(data['suggestions'])}")
    
    # Test 2: Code with bugs
    code_with_bugs = """
def divide_numbers(a, b):
    return a / b

result = divide_numbers(10, 0)
print(f"Result: {result}")
    """
    
    print("\nTest 2: Analysis of code with bugs")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": code_with_bugs, "language": "python", "action": "analyze"}
    )
    
    score2, feedback2 = evaluate_response(
        response, 
        expected_keys=["original_code", "errors", "warnings", "suggestions", "processing_time"],
        success_criteria=lambda data: (
            len(data.get("errors", [])) > 0,
            "Correctly identified error (division by zero)"
        )
    )
    
    for item in feedback2:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n  Analysis Results for Code with Bugs:")
        if "errors" in data and data["errors"]:
            print(f"  - Errors: {len(data['errors'])}")
            for i, error in enumerate(data["errors"][:2], 1):
                print(f"    {i}. {error[:100]}..." if len(error) > 100 else f"    {i}. {error}")
    
    total_score = score + score2
    max_score = 6  # Maximum possible score for the two tests
    percentage = (total_score / max_score) * 100
    
    print(f"\nAnalysis Score: {total_score}/{max_score} ({percentage:.1f}%)")
    return percentage

def check_code_optimization():
    """Test code optimization functionality"""
    print_section("Testing Code Optimization")
    
    # Test with inefficient code
    inefficient_code = """
def find_duplicates(numbers):
    duplicates = []
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j and numbers[i] == numbers[j] and numbers[i] not in duplicates:
                duplicates.append(numbers[i])
    return duplicates

# Test with a list
test_list = [1, 2, 3, 2, 4, 5, 5, 6, 1]
result = find_duplicates(test_list)
print(result)
    """
    
    print("Testing optimization of inefficient code")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": inefficient_code, "language": "python", "action": "optimize"}
    )
    
    score, feedback = evaluate_response(
        response, 
        expected_keys=["original_code", "processed_code", "explanation", "performance_metrics", "processing_time"],
        success_criteria=lambda data: (
            data.get("processed_code") != inefficient_code and "O(n^2)" not in data.get("processed_code", ""),
            "Optimization improved time complexity"
        )
    )
    
    for item in feedback:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n  Optimization Results:")
        print(f"  - Processing Time: {data.get('processing_time', 0):.2f} seconds")
        
        if "performance_metrics" in data and data["performance_metrics"]:
            metrics = data["performance_metrics"]
            if "summary" in metrics:
                print(f"  - Summary: {metrics['summary']}")
            if "key_optimizations" in metrics and metrics["key_optimizations"]:
                print("  - Key Optimizations:")
                for i, opt in enumerate(metrics["key_optimizations"][:3], 1):
                    print(f"    {i}. {opt}")
    
    max_score = 4  # Maximum possible score
    percentage = (score / max_score) * 100
    
    print(f"\nOptimization Score: {score}/{max_score} ({percentage:.1f}%)")
    return percentage

def check_code_fixing():
    """Test code fixing functionality"""
    print_section("Testing Code Fixing")
    
    # Test with buggy code
    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# This will cause a division by zero error
result = calculate_average([])
print(f"Average: {result}")
    """
    
    print("Testing fixing of buggy code")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": buggy_code, "language": "python", "action": "fix"}
    )
    
    # Define success criteria for fixed code
    def is_fixed_properly(data):
        fixed_code = data.get("processed_code", "")
        # Check if fixed code handles empty list case
        return (
            "if" in fixed_code and "len" in fixed_code and ("return 0" in fixed_code or "return None" in fixed_code or "ZeroDivision" in fixed_code),
            "Fixed code handles the empty list case"
        )
    
    score, feedback = evaluate_response(
        response, 
        expected_keys=["original_code", "processed_code", "explanation", "processing_time"],
        success_criteria=is_fixed_properly
    )
    
    for item in feedback:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n  Fix Results:")
        print(f"  - Processing Time: {data.get('processing_time', 0):.2f} seconds")
        if "explanation" in data and data["explanation"]:
            explanation = data["explanation"]
            print(f"  - Explanation: {explanation[:150]}..." if len(explanation) > 150 else f"  - Explanation: {explanation}")
    
    # Test with syntax error
    syntax_error_code = """
def calculate_sum(a, b
    return a + b

result = calculate_sum(5, 10)
print(result)
    """
    
    print("\nTesting fixing of code with syntax error")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": syntax_error_code, "language": "python", "action": "fix"}
    )
    
    # Define success criteria for fixed syntax
    def is_syntax_fixed(data):
        fixed_code = data.get("processed_code", "")
        # Check if fixed code has proper syntax
        return (
            "def calculate_sum(a, b):" in fixed_code and "return a + b" in fixed_code,
            "Fixed the syntax error (missing parenthesis)"
        )
    
    score2, feedback2 = evaluate_response(
        response, 
        expected_keys=["original_code", "processed_code", "explanation", "processing_time"],
        success_criteria=is_syntax_fixed
    )
    
    for item in feedback2:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n  Syntax Fix Results:")
        print(f"  - Processing Time: {data.get('processing_time', 0):.2f} seconds")
    
    total_score = score + score2
    max_score = 8  # Maximum possible score for the two tests
    percentage = (total_score / max_score) * 100
    
    print(f"\nFix Code Score: {total_score}/{max_score} ({percentage:.1f}%)")
    return percentage

def check_code_hints():
    """Test code hints functionality"""
    print_section("Testing Code Hints")
    
    # Test with suboptimal code
    suboptimal_code = """
# Find prime numbers up to n
def find_primes(n):
    primes = []
    for num in range(2, n + 1):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

# Test the function
prime_list = find_primes(100)
print(prime_list)
    """
    
    print("Testing hints for suboptimal code")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": suboptimal_code, "language": "python", "action": "hint"}
    )
    
    score, feedback = evaluate_response(
        response, 
        expected_keys=["original_code", "hints", "processing_time"],
        success_criteria=lambda data: (
            len(data.get("hints", [])) >= 2,
            f"Provided {len(data.get('hints', []))} hints for code improvement"
        )
    )
    
    for item in feedback:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n  Hint Results:")
        print(f"  - Processing Time: {data.get('processing_time', 0):.2f} seconds")
        if "hints" in data and data["hints"]:
            print("  - Hints:")
            for i, hint in enumerate(data["hints"][:3], 1):
                print(f"    {i}. {hint}")
    
    max_score = 4  # Maximum possible score
    percentage = (score / max_score) * 100
    
    print(f"\nHint Score: {score}/{max_score} ({percentage:.1f}%)")
    return percentage

def check_code_execution():
    """Test code execution functionality"""
    print_section("Testing Code Execution")
    
    # Test 1: Basic execution
    basic_code = """
def greet(name):
    return f"Hello, {name}!"

message = greet("World")
print(message)
    """
    
    print("Test 1: Basic code execution")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": basic_code, "language": "python", "action": "execute"}
    )
    
    score, feedback = evaluate_response(
        response, 
        expected_keys=["original_code", "execution_result", "processing_time"],
        success_criteria=lambda data: (
            "Hello, World!" in data.get("execution_result", {}).get("stdout", ""),
            "Output contains expected greeting message"
        )
    )
    
    for item in feedback:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        if "execution_result" in data:
            print("\n  Execution Results:")
            print(f"  - Exit Code: {data['execution_result'].get('exit_code', 'N/A')}")
            print(f"  - Execution Time: {data['execution_result'].get('execution_time', 0):.4f} seconds")
            stdout = data['execution_result'].get('stdout', '')
            print(f"  - Output: {stdout[:100]}" + ("..." if len(stdout) > 100 else ""))
    
    # Test 2: Execution with input
    input_code = """
name = input("Enter your name: ")
age = input("Enter your age: ")
print(f"Hello, {name}! You are {age} years old.")
    """
    
    print("\nTest 2: Execution with input")
    response = requests.post(
        f"{API_URL}/code",
        json={
            "code": input_code, 
            "language": "python", 
            "action": "execute", 
            "inputs": ["Alice", "30"]
        }
    )
    
    score2, feedback2 = evaluate_response(
        response, 
        expected_keys=["original_code", "execution_result", "processing_time"],
        success_criteria=lambda data: (
            "Hello, Alice! You are 30 years old." in data.get("execution_result", {}).get("stdout", ""),
            "Successfully handled inputs during execution"
        )
    )
    
    for item in feedback2:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        if "execution_result" in data:
            print("\n  Execution with Input Results:")
            stdout = data['execution_result'].get('stdout', '')
            print(f"  - Output: {stdout[:100]}" + ("..." if len(stdout) > 100 else ""))
    
    # Test 3: Execution with error
    error_code = """
def divide(a, b):
    return a / b

result = divide(10, 0)
print(f"Result: {result}")
    """
    
    print("\nTest 3: Execution with error")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": error_code, "language": "python", "action": "execute"}
    )
    
    score3, feedback3 = evaluate_response(
        response, 
        expected_keys=["original_code", "execution_result", "processing_time"],
        success_criteria=lambda data: (
            "ZeroDivisionError" in data.get("execution_result", {}).get("stderr", ""),
            "Properly reported division by zero error"
        )
    )
    
    for item in feedback3:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        if "execution_result" in data:
            print("\n  Execution with Error Results:")
            stderr = data['execution_result'].get('stderr', '')
            print(f"  - Error: {stderr[:100]}" + ("..." if len(stderr) > 100 else ""))
    
    # Test 4: Visualization code execution
    viz_code = """
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(8, 4))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.savefig('sine_wave.png')
    """
    
    print("\nTest 4: Visualization code execution")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": viz_code, "language": "python", "action": "execute"}
    )
    
    score4, feedback4 = evaluate_response(
        response, 
        expected_keys=["original_code", "execution_result", "processing_time"],
        success_criteria=lambda data: (
            data.get("execution_result", {}).get("exit_code", -1) == 0,
            "Visualization code executed without errors"
        )
    )
    
    for item in feedback4:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        if "execution_result" in data:
            print("\n  Visualization Execution Results:")
            print(f"  - Exit Code: {data['execution_result'].get('exit_code', 'N/A')}")
            print(f"  - Execution Time: {data['execution_result'].get('execution_time', 0):.4f} seconds")
    
    # Test 5: Machine learning code execution
    ml_code = """
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load data
iris = load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate model
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy:.4f}")
    """
    
    print("\nTest 5: Machine learning code execution")
    response = requests.post(
        f"{API_URL}/code",
        json={"code": ml_code, "language": "python", "action": "execute"}
    )
    
    score5, feedback5 = evaluate_response(
        response, 
        expected_keys=["original_code", "execution_result", "processing_time"],
        success_criteria=lambda data: (
            "Accuracy:" in data.get("execution_result", {}).get("stdout", ""),
            "ML code execution produced accuracy results"
        )
    )
    
    for item in feedback5:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        if "execution_result" in data:
            print("\n  ML Execution Results:")
            stdout = data['execution_result'].get('stdout', '')
            print(f"  - Output: {stdout}")
    
    # Calculate total score
    total_score = score + score2 + score3 + score4 + score5
    max_score = 20  # Maximum possible score for the five tests
    percentage = (total_score / max_score) * 100
    
    print(f"\nExecution Score: {total_score}/{max_score} ({percentage:.1f}%)")
    return percentage

def check_context_aware_fixing():
    """Test context-aware code fixing"""
    print_section("Testing Context-Aware Fixing")
    
    # Test with error context
    buggy_code = """
def process_data(data):
    result = []
    for item in data:
        value = item['value']
        result.append(value * 2)
    return result

sample_data = [
    {'id': 1, 'name': 'Item 1'},
    {'id': 2, 'name': 'Item 2'}
]

processed = process_data(sample_data)
print(processed)
    """
    
    error_message = "KeyError: 'value'"
    
    print("Testing context-aware fixing with error message")
    response = requests.post(
        f"{API_URL}/code/fix-with-context",
        json={
            "code": buggy_code, 
            "language": "python", 
            "error_message": error_message
        }
    )
    
    score, feedback = evaluate_response(
        response, 
        expected_keys=["original_code", "fixed_code", "explanation", "processing_time"],
        success_criteria=lambda data: (
            "try" in data.get("fixed_code", "") or "if" in data.get("fixed_code", "") and "'value'" in data.get("fixed_code", ""),
            "Fixed code handles missing 'value' key properly"
        )
    )
    
    for item in feedback:
        print(f"  {item}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n  Context-Aware Fix Results:")
        print(f"  - Processing Time: {data.get('processing_time', 0):.2f} seconds")
        
        if "explanation" in data:
            explanation = data["explanation"]
            print(f"  - Explanation: {explanation[:150]}..." if len(explanation) > 150 else f"  - Explanation: {explanation}")
    
    max_score = 4  # Maximum possible score
    percentage = (score / max_score) * 100
    
    print(f"\nContext-Aware Fix Score: {score}/{max_score} ({percentage:.1f}%)")
    return percentage

def check_error_handling():
    """Test error handling for various Python exceptions"""
    print_section("Testing Error Handling (Runtime & Syntax)")
    tests = [
        ("SyntaxError", '''def broken_func(:\n    pass''', "syntax error", "SyntaxError"),
        ("NameError", '''print(undeclared_var)''', "name error", "NameError"),
        ("TypeError", '''a = 5\nb = 'str'\nprint(a + b)''', "type error", "TypeError"),
        ("IndexError", '''lst = [1,2,3]\nprint(lst[10])''', "index error", "IndexError"),
        ("KeyError", '''d = {'a': 1}\nprint(d['b'])''', "key error", "KeyError"),
        ("ZeroDivisionError", '''print(1/0)''', "zero division", "ZeroDivisionError"),
        ("FileNotFoundError", '''open('nonexistent_file.txt', 'r')''', "file not found", "FileNotFoundError"),
        ("CustomException", '''class MyEx(Exception): pass\nraise MyEx('custom!')''', "custom exception", "MyEx"),
        ("RecursionError", '''def f(): return f()\nf()''', "recursion error", "RecursionError"),
        ("MemoryError", '''a = []\nwhile True: a.append('A'*10**6)''', "memory error", "MemoryError"),
    ]
    score = 0
    max_score = len(tests)
    for name, code, desc, expected in tests:
        print(f"Test: {name}")
        response = requests.post(
            f"{API_URL}/code",
            json={"code": code, "language": "python", "action": "execute"}
        )
        def criteria(data):
            stderr = data.get("execution_result", {}).get("stderr", "")
            stdout = data.get("execution_result", {}).get("stdout", "")
            found = expected in stderr or expected in stdout or "[FixLoop] MemoryError" in stderr or "[FixLoop] MemoryError" in stdout
            if name == "MemoryError" and not found:
                print("  [WARN] MemoryError was not detected. This test may not be reliable on all systems.")
            return (found, f"Expected error '{expected}' found in output" if found else f"Expected error '{expected}' NOT found in output")
        s, feedback = evaluate_response(
            response,
            expected_keys=["original_code", "execution_result", "processing_time"],
            success_criteria=criteria
        )
        score += s
        for item in feedback:
            print(f"  {item}")
        if response.status_code == 200:
            data = response.json()
            stderr = data.get("execution_result", {}).get("stderr", "")
            print(f"  - Error Output: {stderr[:100]}" + ("..." if len(stderr) > 100 else ""))
    percentage = min((score / (max_score * 4)) * 100, 100)
    print(f"\nError Handling Score: {score}/{max_score*4} ({percentage:.1f}%)")
    return percentage

def check_file_io():
    """Test file I/O operations and error scenarios"""
    print_section("Testing File I/O Operations")
    tests = [
        ("File Write/Read", '''with open('testfile.txt', 'w') as f:\n    f.write('hello')\nwith open('testfile.txt', 'r') as f:\n    print(f.read())''', "hello"),
        ("FileNotFoundError", '''with open('no_such_file.txt', 'r') as f:\n    print(f.read())''', "FileNotFoundError"),
        ("IOError", '''import os\nos.chmod('testfile.txt', 0o000)\ntry:\n    with open('testfile.txt', 'r') as f:\n        print(f.read())\nfinally:\n    os.chmod('testfile.txt', 0o644)''', "PermissionError"),
        ("Large File", '''with open('largefile.txt', 'w') as f:\n    f.write('A'*10**7)\nwith open('largefile.txt', 'r') as f:\n    print(len(f.read()))''', "10000000"),
    ]
    score = 0
    max_score = len(tests)
    for name, code, expected in tests:
        print(f"Test: {name}")
        # Remove file if it exists from previous runs
        if name == "Large File" and os.path.exists('largefile.txt'):
            os.remove('largefile.txt')
        if name == "File Write/Read" and os.path.exists('testfile.txt'):
            os.remove('testfile.txt')
        response = requests.post(
            f"{API_URL}/code",
            json={"code": code, "language": "python", "action": "execute"}
        )
        def criteria(data):
            out = data.get("execution_result", {}).get("stdout", "")
            err = data.get("execution_result", {}).get("stderr", "")
            if name == "File Write/Read":
                found = expected in out
                return (found, "File written and read successfully" if found else "File write/read failed")
            elif name == "Large File":
                found = expected in out
                return (found, "Large file read successfully" if found else "Large file read failed")
            else:
                found = expected in err
                return (found, f"Properly reported {expected}" if found else f"Did not report {expected}")
        s, feedback = evaluate_response(
            response,
            expected_keys=["original_code", "execution_result", "processing_time"],
            success_criteria=criteria
        )
        score += s
        for item in feedback:
            print(f"  {item}")
        if name == "Large File" and os.path.exists('largefile.txt'):
            print(f"  - Large file exists: largefile.txt")
        if response.status_code == 200:
            data = response.json()
            stdout = data.get("execution_result", {}).get("stdout", "")
            stderr = data.get("execution_result", {}).get("stderr", "")
            print(f"  - Output: {stdout[:100]}" + ("..." if len(stdout) > 100 else ""))
            print(f"  - Error: {stderr[:100]}" + ("..." if len(stderr) > 100 else ""))
    percentage = min((score / (max_score * 4)) * 100, 100)
    print(f"\nFile I/O Score: {score}/{max_score*4} ({percentage:.1f}%)")
    return percentage

def check_visualization():
    """Test data visualization code execution and plot interpretation"""
    print_section("Testing Data Visualization Integration")
    tests = [
        ("Matplotlib Line Plot", '''import matplotlib.pyplot as plt\nplt.plot([1,2,3],[4,5,6])\nplt.title('Test Plot')\nplt.savefig('test_plot.png')\nprint('Plot saved!')''', "Plot saved!", "test_plot.png"),
        ("Seaborn Histogram", '''import seaborn as sns\nimport matplotlib.pyplot as plt\ndata = [1,2,2,3,3,3,4,4,4,4]\nsns.histplot(data)\nplt.savefig('hist.png')\nprint('Histogram saved!')''', "Histogram saved!", "hist.png"),
    ]
    score = 0
    max_score = len(tests)
    for name, code, expected_out, expected_file in tests:
        print(f"Test: {name}")
        # Remove file if it exists from previous runs
        if os.path.exists(expected_file):
            os.remove(expected_file)
        response = requests.post(
            f"{API_URL}/code",
            json={"code": code, "language": "python", "action": "execute"}
        )
        def criteria(data):
            out = data.get("execution_result", {}).get("stdout", "")
            file_found = os.path.exists(expected_file)
            out_found = expected_out in out
            found = (out_found and file_found) or file_found
            return (found, f"Visualization code executed and file {expected_file} generated" if found else f"Visualization or file {expected_file} not found in output")
        s, feedback = evaluate_response(
            response,
            expected_keys=["original_code", "execution_result", "processing_time"],
            success_criteria=criteria
        )
        score += s
        for item in feedback:
            print(f"  {item}")
        if os.path.exists(expected_file):
            print(f"  - Plot file exists: {expected_file}")
        if response.status_code == 200:
            data = response.json()
            stdout = data.get("execution_result", {}).get("stdout", "")
            print(f"  - Output: {stdout[:100]}" + ("..." if len(stdout) > 100 else ""))
    percentage = min((score / (max_score * 4)) * 100, 100)
    print(f"\nVisualization Score: {score}/{max_score*4} ({percentage:.1f}%)")
    return percentage

def check_ml_dl_nlp():
    """Test ML/DL/NLP code execution, dependency handling, and output interpretation"""
    print_section("Testing ML/DL/NLP Code Execution")
    tests = [
        ("scikit-learn", '''from sklearn.datasets import load_iris\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score\nX, y = load_iris(return_X_y=True)\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\nmodel = RandomForestClassifier()\nmodel.fit(X_train, y_train)\npreds = model.predict(X_test)\nprint('Accuracy:', accuracy_score(y_test, preds))''', "Accuracy:"),
        ("TensorFlow", '''try:\n import tensorflow as tf\n print('TF Version:', tf.__version__)\nexcept ImportError:\n print('TensorFlow not installed')''', "TF Version:"),
        ("PyTorch", '''try:\n import torch\n print('Torch Version:', torch.__version__)\nexcept ImportError:\n print('PyTorch not installed')''', "Torch Version:"),
        ("spaCy", '''try:\n import spacy\n print('spaCy Version:', spacy.__version__)\nexcept ImportError:\n print('spaCy not installed')''', "spaCy Version:"),
        ("NLTK", '''try:\n import nltk\n print('NLTK Version:', nltk.__version__)\nexcept ImportError:\n print('NLTK not installed')''', "NLTK Version:"),
    ]
    pip_map = {
        "TensorFlow": "tensorflow",
        "PyTorch": "torch",
        "spaCy": "spacy",
        "NLTK": "nltk"
    }
    score = 0
    max_score = len(tests)
    for name, code, expected in tests:
        print(f"Test: {name}")
        response = requests.post(
            f"{API_URL}/code",
            json={"code": code, "language": "python", "action": "execute"}
        )
        def criteria(data):
            out = data.get("execution_result", {}).get("stdout", "")
            if "not installed" in out:
                pkg = pip_map.get(name, name.lower())
                return (False, f"{name} not installed. To install, run: pip install {pkg}")
            found = expected in out
            return (found, f"{name} code executed and output present" if found else f"{name} output not found")
        s, feedback = evaluate_response(
            response,
            expected_keys=["original_code", "execution_result", "processing_time"],
            success_criteria=criteria
        )
        score += s
        for item in feedback:
            print(f"  {item}")
        if response.status_code == 200:
            data = response.json()
            stdout = data.get("execution_result", {}).get("stdout", "")
            print(f"  - Output: {stdout[:100]}" + ("..." if len(stdout) > 100 else ""))
            # Summarize key metrics if present
            if name == "scikit-learn" and "Accuracy:" in stdout:
                acc_line = [line for line in stdout.splitlines() if "Accuracy:" in line]
                if acc_line:
                    print(f"  - ML Metric: {acc_line[0]}")
    percentage = min((score / (max_score * 4)) * 100, 100)
    print(f"\nML/DL/NLP Score: {score}/{max_score*4} ({percentage:.1f}%)")
    return percentage

def check_edge_case_handling():
    """Test that code fixes always handle empty lists, dicts, and sets."""
    print_section("Testing Edge Case Handling (Empty Lists/Dicts/Sets)")
    test_cases = [
        ("Empty List", '''def sum_list(numbers):\n    return sum(numbers)''', 'def sum_list(numbers):', 'if not numbers'),
        ("Empty Dict", '''def get_keys(d):\n    return list(d.keys())''', 'def get_keys(d):', 'if not d'),
        ("Empty Set", '''def count_set(s):\n    return len(s)''', 'def count_set(s):', 'if not s'),
    ]
    score = 0
    for name, code, func_def, expected_check in test_cases:
        print(f"\nTest: {name}")
        # Simulate fix_code API call (replace with actual call in real system)
        from fixloop import fix_code
        import asyncio
        result = asyncio.run(fix_code(code, 'python'))
        fixed_code = result['fixed_code'] if isinstance(result, dict) else result
        if expected_check in fixed_code:
            print(f"[OK] Edge case check found in fix for {name}.")
            score += 1
        else:
            print(f"[FAIL] Edge case check missing in fix for {name}.")
            print(f"Fixed code:\n{fixed_code}")
    percent = (score / len(test_cases)) * 100
    print(f"\nEdge Case Handling Score: {percent:.1f}%")
    return percent

def generate_evaluation_report(scores):
    """Generate and display the overall evaluation report"""
    print_section("FixLoop Evaluation Report")
    # Cap all scores at 100%
    capped_scores = {k: min(100.0, v) for k, v in scores.items()}
    overall_score = sum(capped_scores.values()) / len(capped_scores)
    
    # Create ratings for each feature
    ratings = {}
    for feature, score in capped_scores.items():
        if score >= 90:
            ratings[feature] = "Excellent"
        elif score >= 80:
            ratings[feature] = "Very Good"
        elif score >= 70:
            ratings[feature] = "Good"
        elif score >= 60:
            ratings[feature] = "Satisfactory"
        elif score >= 50:
            ratings[feature] = "Needs Improvement"
        else:
            ratings[feature] = "Poor"
    
    # Overall rating
    if overall_score >= 90:
        overall_rating = "Excellent"
    elif overall_score >= 80:
        overall_rating = "Very Good"
    elif overall_score >= 70:
        overall_rating = "Good"
    elif overall_score >= 60:
        overall_rating = "Satisfactory"
    elif overall_score >= 50:
        overall_rating = "Needs Improvement"
    else:
        overall_rating = "Poor"
    
    # Create report table
    table_data = []
    for feature, score in capped_scores.items():
        feature_name = feature.replace("_", " ").title()
        table_data.append([feature_name, f"{score:.1f}%", ratings[feature]])
    
    # Add overall score
    table_data.append(["Overall", f"{overall_score:.1f}%", overall_rating])
    
    # Print table
    print(tabulate(table_data, headers=["Feature", "Score", "Rating"], tablefmt="grid"))
    
    # Create and save a chart
    try:
        features = [key.replace("_", " ").title() for key in capped_scores.keys()]
        scores_values = list(capped_scores.values())
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(features, scores_values, color='skyblue')
        
        # Add overall score
        plt.axhline(y=overall_score, color='red', linestyle='--', label=f'Overall: {overall_score:.1f}%')
        
        # Add score labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', rotation=0)
        
        plt.ylim(0, 105)
        plt.xlabel('Features')
        plt.ylabel('Score (%)')
        plt.title('FixLoop Evaluation Results')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.legend()
        plt.savefig('fixloop_evaluation.png')
        print("\nEvaluation chart saved as 'fixloop_evaluation.png'")
    except Exception as e:
        print(f"\nCould not generate evaluation chart: {str(e)}")
    
    # Overall conclusion
    print("\nEvaluation Conclusion:")
    if overall_score >= 80:
        print("FixLoop is a high-quality code assistant with strong capabilities across all tested areas.")
    elif overall_score >= 70:
        print("FixLoop is a good code assistant with solid performance in most areas, but with room for improvement.")
    elif overall_score >= 60:
        print("FixLoop is a satisfactory code assistant but needs significant improvements in several areas.")
    else:
        print("FixLoop needs major improvements to be considered reliable for production use.")
    
    # Specific strengths and weaknesses
    strengths = [feature for feature, score in capped_scores.items() if score >= 75]
    weaknesses = [feature for feature, score in capped_scores.items() if score < 60]
    
    if strengths:
        print("\nKey Strengths:")
        for strength in strengths:
            print(f"- {strength.replace('_', ' ').title()}")
    
    if weaknesses:
        print("\nAreas for Improvement:")
        for weakness in weaknesses:
            print(f"- {weakness.replace('_', ' ').title()}")

def main():
    # Wait for server to start
    print("Waiting for FixLoop server to start...")
    time.sleep(5)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            print("Server is not running. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server. Please make sure it's running.")
        return
    
    print("Server is running. Starting evaluation...\n")
    
    # Run all tests and collect scores
    scores = {}
    
    scores["code_analysis"] = check_code_analysis()
    scores["code_optimization"] = check_code_optimization()
    scores["code_fixing"] = check_code_fixing()
    scores["code_hints"] = check_code_hints()
    scores["code_execution"] = check_code_execution()
    scores["context_aware_fixing"] = check_context_aware_fixing()
    scores["error_handling"] = check_error_handling()
    scores["file_io"] = check_file_io()
    scores["visualization"] = check_visualization()
    scores["ml_dl_nlp"] = check_ml_dl_nlp()
    scores["edge_case_handling"] = check_edge_case_handling()
    
    # Generate evaluation report
    generate_evaluation_report(scores)

if __name__ == "__main__":
    main() 