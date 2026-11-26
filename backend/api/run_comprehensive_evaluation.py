#!/usr/bin/env python3
"""
Comprehensive Evaluation Script for FixLoop
================================================
This script tests all the major functionality of FixLoop:
1. Analysis of code
2. Code optimization
3. Code fixing
4. Execution with error handling
5. Data visualization support
6. ML/DL/NLP code handling
7. Exception handling
8. Hint generation
9. API performance
"""

import requests
import json
import time
import os
import sys
try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from tabulate import tabulate
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: Visualization libraries not available. Install matplotlib, numpy, pandas, and tabulate for visualization.")

# API Configuration
API_URL = "http://localhost:8000/api"
OUTPUT_DIR = "evaluation_results"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test cases
ANALYSIS_TEST = """
def calculate_factorial(n):
    if n == 0:
        return 1
    else:
        return n * calculate_factorial(n-1)

# Calculate factorials for numbers 1 to 5
for i in range(1, 6):
    print(f"Factorial of {i} is {calculate_factorial(i)}")
"""

OPTIMIZATION_TEST = """
def find_duplicates(numbers):
    duplicates = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j] and numbers[i] not in duplicates:
                duplicates.append(numbers[i])
    return duplicates

# Test with a large list with duplicates
test_list = [1, 2, 3, 4, 5, 1, 2, 3, 6, 7, 8, 9, 9, 10] * 10
result = find_duplicates(test_list)
print(f"Found {len(result)} duplicates: {result}")
"""

FIX_TEST = """
def divide_numbers(a, b):
    return a / b

# This will cause a division by zero error
result = divide_numbers(10, 0)
print(f"Result: {result}")
"""

EXECUTION_TEST = """
def calculate_sum(numbers):
    return sum(numbers)

nums = [1, 2, 3, 4, 5]
result = calculate_sum(nums)
print(f"Sum of {nums} is {result}")
"""

EXCEPTION_TEST = """
def process_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except IOError as e:
        print(f"Error: I/O error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return None

content = process_file("nonexistent_file.txt")
if content:
    print(f"File content: {content}")
else:
    print("Couldn't read file content.")
"""

VISUALIZATION_TEST = """
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y1, label='sin(x)')
plt.plot(x, y2, label='cos(x)')
plt.title('Sine and Cosine Functions')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.show()
"""

ML_TEST = """
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate model
accuracy = accuracy_score(y_test, predictions)
report = classification_report(y_test, predictions)

print(f"Accuracy: {accuracy:.4f}")
print("Classification Report:")
print(report)
"""

COMPLEX_ERROR_TEST = """
class CustomError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

def validate_input(value):
    if not isinstance(value, int):
        raise TypeError("Value must be an integer")
    if value < 0:
        raise ValueError("Value must be positive")
    if value > 100:
        raise CustomError("Value exceeds maximum limit", 101)
    return value

def process_values(values):
    results = []
    error_count = 0
    
    for i, val in enumerate(values):
        try:
            result = validate_input(val)
            results.append(result)
        except TypeError as e:
            print(f"Type error for value at index {i}: {e}")
            error_count += 1
        except ValueError as e:
            print(f"Value error for value at index {i}: {e}")
            error_count += 1
        except CustomError as e:
            print(f"Custom error for value at index {i}: {e.message} (Code: {e.error_code})")
            error_count += 1
    
    return results, error_count

# Test with various values
test_values = [50, -10, "string", 150, 75]
valid_results, error_count = process_values(test_values)

print(f"Valid results: {valid_results}")
print(f"Encountered {error_count} errors")
"""

HINTS_TEST = """
def calculate_average(numbers):
    # This function should calculate the average of a list of numbers
    # TODO: Implement this function
    pass

# Test the function
test_numbers = [10, 20, 30, 40, 50]
avg = calculate_average(test_numbers)
print(f"The average is: {avg}")
"""

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
        feedback.append("✅ API call successful")
    else:
        feedback.append(f"❌ API call failed with status code {response.status_code}")
        return 0, feedback
    
    # Parse JSON response
    try:
        data = response.json()
        score += 1
        feedback.append("✅ Response contains valid JSON")
    except:
        feedback.append("❌ Response doesn't contain valid JSON")
        return score, feedback
    
    # Check for expected keys
    if expected_keys:
        for key in expected_keys:
            if key in data:
                score += 0.5
                feedback.append(f"✅ Response contains expected key: {key}")
            else:
                feedback.append(f"❌ Missing expected key: {key}")
    
    # Check for success criteria if provided
    if success_criteria and callable(success_criteria):
        if success_criteria(data):
            score += 2
            feedback.append("✅ Response meets success criteria")
        else:
            feedback.append("❌ Response doesn't meet success criteria")
    
    # Calculate percentage score
    total_possible = 2  # Base score for successful call and valid JSON
    if expected_keys:
        total_possible += 0.5 * len(expected_keys)
    if success_criteria:
        total_possible += 2
    
    percentage = (score / total_possible) * 100
    
    return percentage, feedback

def check_code_analysis():
    """Test code analysis functionality"""
    print_section("Testing Code Analysis")
    
    response = requests.post(
        f"{API_URL}/code",
        json={"code": ANALYSIS_TEST, "language": "python", "action": "analyze"}
    )
    
    expected_keys = ["original_code", "explanation", "processing_time"]
    
    def success_criteria(data):
        # Check if explanation contains meaningful analysis
        if "explanation" in data and data["explanation"]:
            explanation = data["explanation"].lower()
            return ("factorial" in explanation and 
                    len(explanation) > 100 and 
                    any(term in explanation for term in ["recursion", "recursive", "stack"]))
        return False
    
    score, feedback = evaluate_response(response, expected_keys, success_criteria)
    
    print("Test Results:")
    for fb in feedback:
        print(f"  {fb}")
    
    print(f"\nAnalysis Score: {score:.1f}%")
    
    # Save raw response for reference
    if response.status_code == 200:
        try:
            with open(f"{OUTPUT_DIR}/analysis_response.json", "w") as f:
                json.dump(response.json(), f, indent=2)
            print(f"Raw response saved to {OUTPUT_DIR}/analysis_response.json")
        except:
            print("Failed to save raw response")
    
    return score

def check_code_optimization():
    """Test code optimization functionality"""
    print_section("Testing Code Optimization")
    
    response = requests.post(
        f"{API_URL}/code",
        json={"code": OPTIMIZATION_TEST, "language": "python", "action": "optimize"}
    )
    
    expected_keys = ["original_code", "processed_code", "explanation", "processing_time"]
    
    def success_criteria(data):
        # Check if optimization contains improvements
        if "processed_code" in data and data["processed_code"]:
            optimized_code = data["processed_code"].lower()
            return (len(optimized_code) > 0 and 
                    any(term in optimized_code for term in ["set(", "counter", "dict", "collections"]) and
                    "explanation" in data and len(data["explanation"]) > 50)
        return False
    
    score, feedback = evaluate_response(response, expected_keys, success_criteria)
    
    print("Test Results:")
    for fb in feedback:
        print(f"  {fb}")
    
    print(f"\nOptimization Score: {score:.1f}%")
    
    # Save raw response for reference
    if response.status_code == 200:
        try:
            with open(f"{OUTPUT_DIR}/optimization_response.json", "w") as f:
                json.dump(response.json(), f, indent=2)
            print(f"Raw response saved to {OUTPUT_DIR}/optimization_response.json")
        except:
            print("Failed to save raw response")
    
    return score

def check_code_fixing():
    """Test code fixing functionality"""
    print_section("Testing Code Fixing")
    
    response = requests.post(
        f"{API_URL}/code",
        json={"code": FIX_TEST, "language": "python", "action": "fix"}
    )
    
    expected_keys = ["original_code", "processed_code", "explanation", "processing_time"]
    
    def is_fixed_properly(data):
        # Check if the division by zero error is properly fixed
        if "processed_code" in data and data["processed_code"]:
            fixed_code = data["processed_code"].lower()
            return (len(fixed_code) > 0 and 
                    ("try" in fixed_code or "if" in fixed_code) and
                    any(term in fixed_code for term in ["zero", "!= 0", "> 0", "== 0"]))
        return False
    
    score, feedback = evaluate_response(response, expected_keys, is_fixed_properly)
    
    print("Test Results:")
    for fb in feedback:
        print(f"  {fb}")
    
    print(f"\nCode Fixing Score: {score:.1f}%")
    
    # Save raw response for reference
    if response.status_code == 200:
        try:
            with open(f"{OUTPUT_DIR}/fix_response.json", "w") as f:
                json.dump(response.json(), f, indent=2)
            print(f"Raw response saved to {OUTPUT_DIR}/fix_response.json")
        except:
            print("Failed to save raw response")
    
    return score

def check_code_hints():
    """Test hint generation functionality"""
    print_section("Testing Hint Generation")
    
    response = requests.post(
        f"{API_URL}/code",
        json={"code": HINTS_TEST, "language": "python", "action": "hint"}
    )
    
    expected_keys = ["original_code", "hints", "processing_time"]
    
    def success_criteria(data):
        # Check if hints are meaningful
        if "hints" in data and data["hints"] and isinstance(data["hints"], list):
            hints_text = " ".join(data["hints"]).lower()
            return (len(data["hints"]) > 0 and 
                    any(term in hints_text for term in ["average", "sum", "divide", "len"]))
        return False
    
    score, feedback = evaluate_response(response, expected_keys, success_criteria)
    
    print("Test Results:")
    for fb in feedback:
        print(f"  {fb}")
    
    print(f"\nHint Generation Score: {score:.1f}%")
    
    # Save raw response for reference
    if response.status_code == 200:
        try:
            with open(f"{OUTPUT_DIR}/hints_response.json", "w") as f:
                json.dump(response.json(), f, indent=2)
            print(f"Raw response saved to {OUTPUT_DIR}/hints_response.json")
        except:
            print("Failed to save raw response")
    
    return score

def check_code_execution():
    """Test code execution functionality"""
    print_section("Testing Code Execution")
    
    # Test 1: Basic execution
    print("Test 1: Basic code execution")
    basic_response = requests.post(
        f"{API_URL}/code",
        json={"code": EXECUTION_TEST, "language": "python", "action": "execute"}
    )
    
    basic_expected_keys = ["original_code", "execution_result", "processing_time"]
    
    def basic_success_criteria(data):
        if "execution_result" in data and data["execution_result"]:
            exec_result = data["execution_result"]
            return (isinstance(exec_result, dict) and 
                    "stdout" in exec_result and 
                    "Sum of [1, 2, 3, 4, 5] is 15" in exec_result.get("stdout", ""))
        return False
    
    basic_score, basic_feedback = evaluate_response(basic_response, basic_expected_keys, basic_success_criteria)
    
    print("\nBasic Execution Results:")
    for fb in basic_feedback:
        print(f"  {fb}")
    
    print(f"\nBasic Execution Score: {basic_score:.1f}%")
    
    # Test 2: Exception handling
    print("\nTest 2: Exception handling in execution")
    exception_response = requests.post(
        f"{API_URL}/code",
        json={"code": EXCEPTION_TEST, "language": "python", "action": "execute"}
    )
    
    exception_expected_keys = ["original_code", "execution_result", "processing_time"]
    
    def exception_success_criteria(data):
        if "execution_result" in data and data["execution_result"]:
            exec_result = data["execution_result"]
            return (isinstance(exec_result, dict) and 
                    "stdout" in exec_result and 
                    "File 'nonexistent_file.txt' not found" in exec_result.get("stdout", ""))
        return False
    
    exception_score, exception_feedback = evaluate_response(exception_response, exception_expected_keys, exception_success_criteria)
    
    print("\nException Handling Results:")
    for fb in exception_feedback:
        print(f"  {fb}")
    
    print(f"\nException Handling Score: {exception_score:.1f}%")
    
    # Test 3: Complex error handling
    print("\nTest 3: Complex error handling in execution")
    complex_response = requests.post(
        f"{API_URL}/code",
        json={"code": COMPLEX_ERROR_TEST, "language": "python", "action": "execute"}
    )
    
    complex_expected_keys = ["original_code", "execution_result", "processing_time"]
    
    def complex_success_criteria(data):
        if "execution_result" in data and data["execution_result"]:
            exec_result = data["execution_result"]
            stdout = exec_result.get("stdout", "")
            return (isinstance(exec_result, dict) and
                    "stdout" in exec_result and
                    "Valid results: [50, 75]" in stdout and
                    "Encountered 3 errors" in stdout)
        return False
    
    complex_score, complex_feedback = evaluate_response(complex_response, complex_expected_keys, complex_success_criteria)
    
    print("\nComplex Error Handling Results:")
    for fb in complex_feedback:
        print(f"  {fb}")
    
    print(f"\nComplex Error Handling Score: {complex_score:.1f}%")
    
    # Test 4: Visualization support
    viz_score = 0
    if VISUALIZATION_AVAILABLE:
        print("\nTest 4: Visualization code support")
        viz_response = requests.post(
            f"{API_URL}/code",
            json={"code": VISUALIZATION_TEST, "language": "python", "action": "execute"}
        )
        
        viz_expected_keys = ["original_code", "execution_result", "processing_time"]
        
        def viz_success_criteria(data):
            if "execution_result" in data and data["execution_result"]:
                exec_result = data["execution_result"]
                return (isinstance(exec_result, dict) and
                        "stdout" in exec_result and
                        (("visualizations" in exec_result.get("stdout", "").lower()) or
                         ("plot" in exec_result.get("stdout", "").lower()) or
                         ("saving" in exec_result.get("stdout", "").lower())))
            return False
        
        viz_score, viz_feedback = evaluate_response(viz_response, viz_expected_keys, viz_success_criteria)
        
        print("\nVisualization Support Results:")
        for fb in viz_feedback:
            print(f"  {fb}")
        
        print(f"\nVisualization Support Score: {viz_score:.1f}%")
        
        # Save raw response
        if viz_response.status_code == 200:
            try:
                with open(f"{OUTPUT_DIR}/visualization_execution_response.json", "w") as f:
                    json.dump(viz_response.json(), f, indent=2)
            except:
                print("Failed to save visualization execution response")
    else:
        print("\nSkipping Visualization test - required libraries not installed")
        viz_score = 0  # Default score
    
    # Test 5: ML code execution (skip if sklearn not installed)
    ml_score = 0
    try:
        import sklearn
        print("\nTest 5: Machine Learning code support")
        ml_response = requests.post(
            f"{API_URL}/code",
            json={"code": ML_TEST, "language": "python", "action": "execute"}
        )
        
        ml_expected_keys = ["original_code", "execution_result", "processing_time"]
        
        def ml_success_criteria(data):
            if "execution_result" in data and data["execution_result"]:
                exec_result = data["execution_result"]
                return (isinstance(exec_result, dict) and
                        "stdout" in exec_result and
                        "Accuracy:" in exec_result.get("stdout", "") and
                        "Classification Report:" in exec_result.get("stdout", ""))
            return False
        
        ml_score, ml_feedback = evaluate_response(ml_response, ml_expected_keys, ml_success_criteria)
        
        print("\nMachine Learning Support Results:")
        for fb in ml_feedback:
            print(f"  {fb}")
        
        print(f"\nMachine Learning Support Score: {ml_score:.1f}%")
        
        # Save raw response
        if ml_response.status_code == 200:
            try:
                with open(f"{OUTPUT_DIR}/ml_execution_response.json", "w") as f:
                    json.dump(ml_response.json(), f, indent=2)
            except:
                print("Failed to save ML execution response")
    except ImportError:
        print("\nSkipping ML test - sklearn not installed")
        ml_score = 0  # Default score
    
    # Calculate combined execution score
    # Determine divisor based on which tests were run
    divisor = 3  # Basic, exception, complex always run
    if VISUALIZATION_AVAILABLE:
        divisor += 1
    try:
        import sklearn
        divisor += 1
    except ImportError:
        pass
        
    execution_score = (basic_score + exception_score + complex_score + viz_score + ml_score) / divisor
    print(f"\nOverall Execution Score: {execution_score:.1f}%")
    
    # Save raw responses for reference
    if basic_response.status_code == 200:
        try:
            with open(f"{OUTPUT_DIR}/basic_execution_response.json", "w") as f:
                json.dump(basic_response.json(), f, indent=2)
        except:
            print("Failed to save basic execution response")
    
    if exception_response.status_code == 200:
        try:
            with open(f"{OUTPUT_DIR}/exception_execution_response.json", "w") as f:
                json.dump(exception_response.json(), f, indent=2)
        except:
            print("Failed to save exception execution response")
    
    if complex_response.status_code == 200:
        try:
            with open(f"{OUTPUT_DIR}/complex_execution_response.json", "w") as f:
                json.dump(complex_response.json(), f, indent=2)
        except:
            print("Failed to save complex execution response")
    
    return execution_score

def get_recommendations(scores):
    """Generate recommendations based on scores"""
    recommendations = []
    
    # Add feature-specific recommendations
    if scores['analysis'] < 70:
        recommendations.append("- **Code Analysis**: Improve the depth and accuracy of code analysis, especially for identifying potential issues and edge cases.")
    
    if scores['optimization'] < 70:
        recommendations.append("- **Code Optimization**: Enhance optimization suggestions to provide more efficient alternatives and detailed explanations of improvements.")
    
    if scores['fixing'] < 70:
        recommendations.append("- **Code Fixing**: Improve bug detection and fixing, particularly for common errors like division by zero, index errors, and type handling.")
    
    if scores['hints'] < 70:
        recommendations.append("- **Hint Generation**: Make hints more specific and actionable, with clearer guidance on implementation details.")
    
    if scores['execution'] < 70:
        recommendations.append("- **Code Execution**: Enhance the execution environment's error handling and support for visualization and ML libraries.")
    
    # Add general recommendations
    recommendations.append("- **Error Handling**: Ensure all API endpoints have robust error handling with helpful error messages.")
    recommendations.append("- **Response Time**: Monitor and optimize API response times for better user experience.")
    
    # If no specific recommendations based on low scores
    if not recommendations:
        recommendations.append("- **General Maintenance**: Continue regular updates and enhancements to maintain high performance.")
        recommendations.append("- **Advanced Features**: Consider adding more advanced features such as code refactoring and security analysis.")
    
    return "\n".join(recommendations)

def generate_evaluation_report(scores):
    """Generate and save a comprehensive evaluation report"""
    print_section("Generating Evaluation Report")
    
    # Calculate overall score
    overall_score = sum(scores.values()) / len(scores)
    
    # Create report
    report = f"""
# FixLoop Evaluation Report

## Summary

Overall Score: **{overall_score:.1f}%**

| Feature | Score |
|---------|-------|
| Code Analysis | {scores['analysis']:.1f}% |
| Code Optimization | {scores['optimization']:.1f}% |
| Code Fixing | {scores['fixing']:.1f}% |
| Hint Generation | {scores['hints']:.1f}% |
| Code Execution | {scores['execution']:.1f}% |

## Test Details

### Code Analysis
- Tests the ability to analyze code and provide meaningful insights
- Evaluated factorial calculation code analysis

### Code Optimization
- Tests the ability to optimize inefficient code
- Evaluated duplicate finding algorithm optimization

### Code Fixing
- Tests the ability to fix bugs in code
- Evaluated division by zero error fixing

### Hint Generation
- Tests the ability to provide helpful hints for code improvement
- Evaluated hint generation for an incomplete function

### Code Execution
- Tests the ability to execute code with proper handling of:
  - Basic code execution
  - Exception handling
  - Complex error handling
  - Data visualization code
  - Machine learning code

## Recommendations

Based on the evaluation results, the following areas could be improved:

{get_recommendations(scores)}

## Test Environment
- Test Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
- Python Version: {sys.version.split()[0]}
- Platform: {sys.platform}
"""
    
    # Save report
    report_path = f"{OUTPUT_DIR}/comprehensive_evaluation_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"Evaluation report saved to {report_path}")
    
    # Display summary
    print("\nEvaluation Summary:")
    print(f"Overall Score: {overall_score:.1f}%")
    
    # Create table for console output
    if 'tabulate' in sys.modules:
        table_data = []
        for feature, score in scores.items():
            # Determine rating based on score
            if score >= 90:
                rating = "Excellent"
            elif score >= 80:
                rating = "Good"
            elif score >= 70:
                rating = "Satisfactory"
            elif score >= 50:
                rating = "Needs Improvement"
            else:
                rating = "Poor"
            
            table_data.append([feature.capitalize(), f"{score:.1f}%", rating])
        
        print(tabulate(table_data, headers=["Feature", "Score", "Rating"], tablefmt="grid"))
    else:
        # Simple table format if tabulate not available
        print("\nFeature\t\tScore\t\tRating")
        print("-" * 50)
        for feature, score in scores.items():
            # Determine rating based on score
            if score >= 90:
                rating = "Excellent"
            elif score >= 80:
                rating = "Good"
            elif score >= 70:
                rating = "Satisfactory"
            elif score >= 50:
                rating = "Needs Improvement"
            else:
                rating = "Poor"
            
            print(f"{feature.capitalize()}\t\t{score:.1f}%\t\t{rating}")
    
    # Create visualization of results if matplotlib is available
    if VISUALIZATION_AVAILABLE:
        try:
            features = list(scores.keys())
            feature_scores = list(scores.values())
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(features, feature_scores, color='skyblue')
            
            # Add overall score line
            plt.axhline(y=overall_score, color='r', linestyle='-', label=f'Overall: {overall_score:.1f}%')
            
            # Add score labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom')
            
            plt.ylim(0, 105)  # Set y-axis limit
            plt.ylabel('Score (%)')
            plt.title('FixLoop Evaluation Results')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.legend()
            
            # Save plot
            plt.savefig(f"{OUTPUT_DIR}/evaluation_results.png")
            print(f"Evaluation chart saved to {OUTPUT_DIR}/evaluation_results.png")
        except Exception as e:
            print(f"Failed to create visualization: {e}")
    
    return overall_score

def check_api_health():
    """Check if the API is healthy and running"""
    print_section("Checking API Health")
    
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to API: {e}")
        return False

def main():
    """Run the comprehensive evaluation"""
    print_section("FixLoop Comprehensive Evaluation")
    
    # Check if API is running
    if not check_api_health():
        print("\nError: API is not running or not accessible. Please start the FixLoop server and try again.")
        return
    
    # Run all tests
    scores = {
        'analysis': check_code_analysis(),
        'optimization': check_code_optimization(),
        'fixing': check_code_fixing(),
        'hints': check_code_hints(),
        'execution': check_code_execution()
    }
    
    # Generate evaluation report
    generate_evaluation_report(scores)

if __name__ == "__main__":
    main() 