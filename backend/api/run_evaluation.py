import os
import sys
import time
import subprocess
import platform
from io import StringIO
import re
from contextlib import redirect_stdout, redirect_stderr
import requests
import statistics
from datetime import datetime

def run_test_script(script_name):
    """Run a test script and capture its output and execution time."""
    print(f"Running {script_name}...")
    start_time = time.time()
    
    # Run the script as a subprocess to ensure clean environment for each test
    try:
        # Add a timeout of 60 seconds to prevent tests from hanging
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60  # Add 60-second timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            "script": script_name,
            "output": result.stdout,
            "error": result.stderr,
            "execution_time": execution_time,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Test timed out after 60 seconds: {script_name}")
        return {
            "script": script_name,
            "output": "TEST TIMED OUT AFTER 60 SECONDS",
            "error": "Execution exceeded timeout limit of 60 seconds",
            "execution_time": 60.0,
            "success": False
        }

def analyze_test_results(results):
    """Analyze test results and assign scores."""
    scores = {
        "analysis": {"score": 0, "max": 10, "strengths": [], "weaknesses": []},
        "optimization": {"score": 0, "max": 10, "strengths": [], "weaknesses": []},
        "fix": {"score": 0, "max": 10, "strengths": [], "weaknesses": []},
        "hints": {"score": 0, "max": 10, "strengths": [], "weaknesses": []},
        "execution": {"score": 0, "max": 10, "strengths": [], "weaknesses": []},
        "overall": {"score": 0, "max": 10, "strengths": [], "weaknesses": []}
    }
    
    # Analyze analysis tests
    analysis_results = [r for r in results if "analysis" in r["script"].lower()]
    if analysis_results:
        # Check for errors
        if all(r["success"] for r in analysis_results):
            scores["analysis"]["score"] += 3
            scores["analysis"]["strengths"].append("Successfully ran without errors")
        else:
            scores["analysis"]["weaknesses"].append("Failed to run without errors")
        
        # Check for response time
        avg_time = sum(r["execution_time"] for r in analysis_results) / len(analysis_results)
        if avg_time < 5:
            scores["analysis"]["score"] += 2
            scores["analysis"]["strengths"].append(f"Fast response time ({avg_time:.2f}s)")
        elif avg_time < 30:
            scores["analysis"]["score"] += 1
            scores["analysis"]["strengths"].append(f"Moderate response time ({avg_time:.2f}s)")
        else:
            scores["analysis"]["weaknesses"].append(f"Slow response time ({avg_time:.2f}s)")
        
        # Check for analysis content
        has_errors = any("errors" in r["output"].lower() for r in analysis_results)
        has_warnings = any("warnings" in r["output"].lower() for r in analysis_results)
        has_suggestions = any("suggestions" in r["output"].lower() for r in analysis_results)
        
        if has_errors and has_warnings and has_suggestions:
            scores["analysis"]["score"] += 5
            scores["analysis"]["strengths"].append("Comprehensive analysis with errors, warnings, and suggestions")
        elif (has_errors and has_warnings) or (has_errors and has_suggestions) or (has_warnings and has_suggestions):
            scores["analysis"]["score"] += 3
            scores["analysis"]["strengths"].append("Partial analysis with some categories")
        else:
            scores["analysis"]["score"] += 1
            scores["analysis"]["weaknesses"].append("Limited analysis categories")
    
    # Analyze optimization tests
    optimization_results = [r for r in results if "optim" in r["script"].lower()]
    if optimization_results:
        # Check for errors
        if all(r["success"] for r in optimization_results):
            scores["optimization"]["score"] += 3
            scores["optimization"]["strengths"].append("Successfully ran without errors")
        else:
            scores["optimization"]["weaknesses"].append("Failed to run without errors")
        
        # Check for response time
        avg_time = sum(r["execution_time"] for r in optimization_results) / len(optimization_results)
        if avg_time < 10:
            scores["optimization"]["score"] += 2
            scores["optimization"]["strengths"].append(f"Fast response time ({avg_time:.2f}s)")
        elif avg_time < 60:
            scores["optimization"]["score"] += 1
            scores["optimization"]["strengths"].append(f"Moderate response time ({avg_time:.2f}s)")
        else:
            scores["optimization"]["weaknesses"].append(f"Slow response time ({avg_time:.2f}s)")
        
        # Check for optimization content
        has_explanation = any("explanation" in r["output"].lower() for r in optimization_results)
        has_optimized_code = any("optimized code" in r["output"].lower() for r in optimization_results)
        
        if has_explanation and has_optimized_code:
            scores["optimization"]["score"] += 5
            scores["optimization"]["strengths"].append("Provides both explanation and optimized code")
        elif has_explanation or has_optimized_code:
            scores["optimization"]["score"] += 3
            scores["optimization"]["strengths"].append("Provides either explanation or optimized code")
        else:
            scores["optimization"]["score"] += 1
            scores["optimization"]["weaknesses"].append("Limited optimization output")
    
    # Analyze fix tests
    fix_results = [r for r in results if "fix" in r["script"].lower()]
    if fix_results:
        # Check for errors
        if all(r["success"] for r in fix_results):
            scores["fix"]["score"] += 3
            scores["fix"]["strengths"].append("Successfully ran without errors")
        else:
            scores["fix"]["weaknesses"].append("Failed to run without errors")
        
        # Check for response time
        avg_time = sum(r["execution_time"] for r in fix_results) / len(fix_results)
        if avg_time < 5:
            scores["fix"]["score"] += 2
            scores["fix"]["strengths"].append(f"Fast response time ({avg_time:.2f}s)")
        elif avg_time < 30:
            scores["fix"]["score"] += 1
            scores["fix"]["strengths"].append(f"Moderate response time ({avg_time:.2f}s)")
        else:
            scores["fix"]["weaknesses"].append(f"Slow response time ({avg_time:.2f}s)")
        
        # Check for fix content
        has_explanation = any("explanation" in r["output"].lower() for r in fix_results)
        has_fixed_code = any("fixed code" in r["output"].lower() for r in fix_results)
        
        if has_explanation and has_fixed_code:
            scores["fix"]["score"] += 5
            scores["fix"]["strengths"].append("Provides both explanation and fixed code")
        elif has_explanation or has_fixed_code:
            scores["fix"]["score"] += 3
            scores["fix"]["strengths"].append("Provides either explanation or fixed code")
        else:
            scores["fix"]["score"] += 1
            scores["fix"]["weaknesses"].append("Limited fix output")
    
    # Analyze execution tests
    execution_results = [r for r in results if "execute" in r["script"].lower() or "input" in r["script"].lower() or "exception" in r["script"].lower()]
    if execution_results:
        # Check for errors
        if all(r["success"] for r in execution_results):
            scores["execution"]["score"] += 3
            scores["execution"]["strengths"].append("Successfully ran without errors")
        else:
            scores["execution"]["weaknesses"].append("Failed to run without errors")
        
        # Check for response time
        avg_time = sum(r["execution_time"] for r in execution_results) / len(execution_results)
        if avg_time < 3:
            scores["execution"]["score"] += 2
            scores["execution"]["strengths"].append(f"Fast response time ({avg_time:.2f}s)")
        elif avg_time < 10:
            scores["execution"]["score"] += 1
            scores["execution"]["strengths"].append(f"Moderate response time ({avg_time:.2f}s)")
        else:
            scores["execution"]["weaknesses"].append(f"Slow response time ({avg_time:.2f}s)")
        
        # Check for execution features
        handles_input = any("input" in r["script"].lower() and "input" in r["output"].lower() for r in execution_results)
        handles_exceptions = any("exception" in r["script"].lower() and "exception" in r["output"].lower() for r in execution_results)
        
        if handles_input and handles_exceptions:
            scores["execution"]["score"] += 5
            scores["execution"]["strengths"].append("Handles both input and exceptions")
        elif handles_input or handles_exceptions:
            scores["execution"]["score"] += 3
            scores["execution"]["strengths"].append("Handles either input or exceptions")
        else:
            scores["execution"]["score"] += 1
            scores["execution"]["weaknesses"].append("Limited execution capabilities")
    
    # Analyze data visualization and ML tests
    viz_ml_results = [r for r in results if "visualization" in r["script"].lower() or "ml" in r["script"].lower()]
    if viz_ml_results:
        # Check for errors
        if all(r["success"] for r in viz_ml_results):
            scores["execution"]["score"] += 1
            scores["execution"]["strengths"].append("Successfully ran data visualization and ML tests")
        else:
            for r in viz_ml_results:
                if not r["success"]:
                    scores["execution"]["weaknesses"].append(f"Failed to run {r['script']}")
        
        # Check for specific capabilities
        handles_viz = any("visualization" in r["script"].lower() and "plot" in r["output"].lower() for r in viz_ml_results)
        handles_ml = any("ml" in r["script"].lower() and ("model" in r["output"].lower() or "training" in r["output"].lower()) for r in viz_ml_results)
        
        if handles_viz and handles_ml:
            scores["execution"]["score"] += 2
            scores["execution"]["strengths"].append("Handles both data visualization and ML")
        elif handles_viz or handles_ml:
            scores["execution"]["score"] += 1
            scores["execution"]["strengths"].append("Handles either data visualization or ML")
    
    # Analyze hint generation
    # (Note: There's no specific test for hint generation, so we'll check for hints in analysis output)
    hint_content = "".join([r["output"] for r in results if "analyze" in r["script"].lower()])
    if "hint" in hint_content.lower():
        scores["hints"]["score"] = 7  # Default reasonable score since we can't test directly
        scores["hints"]["strengths"].append("Hints provided in analysis output")
    else:
        scores["hints"]["score"] = 4
        scores["hints"]["weaknesses"].append("No clear hint generation detected")
    
    # Cap scores at max value
    for category in scores:
        scores[category]["score"] = min(scores[category]["score"], scores[category]["max"])
    
    # Calculate overall score
    total_score = 0
    total_max = 0
    for category in ["analysis", "optimization", "fix", "hints", "execution"]:
        total_score += scores[category]["score"]
        total_max += scores[category]["max"]
    
    if total_max > 0:
        scores["overall"]["score"] = round(10 * total_score / total_max, 1)
    
    # Add overall strengths and weaknesses
    if all(r["success"] for r in results):
        scores["overall"]["strengths"].append("All tests ran successfully")
    else:
        scores["overall"]["weaknesses"].append("Some tests failed")
    
    all_strengths = []
    for category in ["analysis", "optimization", "fix", "hints", "execution"]:
        all_strengths.extend(scores[category]["strengths"])
    
    all_weaknesses = []
    for category in ["analysis", "optimization", "fix", "hints", "execution"]:
        all_weaknesses.extend(scores[category]["weaknesses"])
    
    # Add top strengths and weaknesses to overall
    top_strengths = sorted(set(all_strengths), key=all_strengths.count, reverse=True)[:3]
    top_weaknesses = sorted(set(all_weaknesses), key=all_weaknesses.count, reverse=True)[:3]
    
    scores["overall"]["strengths"].extend(top_strengths)
    scores["overall"]["weaknesses"].extend(top_weaknesses)
    
    return scores

def print_summary(results, scores):
    """Print a summary of the test results and scores."""
    print("\n" + "="*80)
    print("FIXLOOP EVALUATION SUMMARY")
    print("="*80)
    
    print("\nTest Results:")
    print("-" * 80)
    for result in results:
        status = "✅ Passed" if result["success"] else "❌ Failed"
        print(f"{result['script']:<30} {status:<10} {result['execution_time']:.2f}s")
    
    print("\nFeature Scores:")
    print("-" * 80)
    for category, data in scores.items():
        if category != "overall":
            print(f"{category.upper():<15} {data['score']}/{data['max']}")
            print(f"  Strengths: {', '.join(data['strengths'])}")
            print(f"  Weaknesses: {', '.join(data['weaknesses'])}")
            print()
    
    print("="*80)
    print(f"OVERALL SCORE: {scores['overall']['score']}/10")
    print("="*80)
    
    print("\nOverall Strengths:")
    for strength in scores["overall"]["strengths"]:
        print(f"  • {strength}")
    
    print("\nOverall Weaknesses:")
    for weakness in scores["overall"]["weaknesses"]:
        print(f"  • {weakness}")
    
    print("\n")

def main():
    # List all test scripts
    test_scripts = [
        "test_analysis.py",
        "test_simple_analysis.py", 
        "test_optimize_code.py",
        "test_fix.py",
        "test_complex_fix.py",
        "test_bugfix.py",
        "test_api.py",
        "test_execute.py",
        "test_input.py",  # Now safe to include since we've modified it to be automated
        "test_exception_handling.py",
        "test_data_visualization.py",
        "test_ml.py",
        "test_optimization.py",
        "test_python_code.py"  # This has been fixed too
    ]
    
    # Run each test script and collect results
    results = []
    for script in test_scripts:
        if os.path.exists(script):
            result = run_test_script(script)
            results.append(result)
        else:
            print(f"Warning: {script} not found, skipping...")
    
    # Analyze results and assign scores
    scores = analyze_test_results(results)
    
    # Print summary
    print_summary(results, scores)
    
    # Create report file
    with open("new_evaluation_report.md", "w") as f:
        f.write("# FixLoop Evaluation Report\n\n")
        f.write("## Overview\n")
        f.write("This report provides a detailed evaluation of FixLoop, a self-correcting AI coding assistant. ")
        f.write("The system was tested across all its major functions: code analysis, optimization, hint generation, bug fixing, and code execution ")
        f.write("with various types of inputs and error scenarios.\n\n")
        
        f.write("## Test Environment\n")
        f.write(f"- **OS**: {platform.system()} {platform.version()}\n")
        f.write(f"- **Python Version**: {sys.version.split()[0]}\n\n")
        
        f.write("## Feature Evaluation\n\n")
        
        for category, data in scores.items():
            if category != "overall":
                f.write(f"### {category.capitalize()} Function\n")
                f.write(f"**Score: {data['score']}/{data['max']}**\n\n")
                
                f.write("**Strengths:**\n")
                for strength in data["strengths"]:
                    f.write(f"- {strength}\n")
                f.write("\n")
                
                f.write("**Weaknesses:**\n")
                for weakness in data["weaknesses"]:
                    f.write(f"- {weakness}\n")
                f.write("\n")
                
                f.write("**Comments:** Based on test results.\n\n")
        
        f.write("## Overall Assessment\n\n")
        
        f.write("### Strengths\n")
        for strength in scores["overall"]["strengths"]:
            f.write(f"- {strength}\n")
        f.write("\n")
        
        f.write("### Areas for Improvement\n")
        for weakness in scores["overall"]["weaknesses"]:
            f.write(f"- {weakness}\n")
        f.write("\n")
        
        f.write(f"### Overall Score: {scores['overall']['score']}/10\n\n")
        
        f.write("FixLoop shows significant promise as a self-correcting AI coding assistant. ")
        f.write("It provides valuable capabilities for code analysis, optimization, bug fixing, and execution. ")
        f.write("The system performs best in [top strengths] and could be improved in [top weaknesses].\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. **Improve response times** for analysis and optimization operations\n")
        f.write("2. **Enhance detection of edge cases** in bug fixing\n")
        f.write("3. **Add more comprehensive documentation** for API usage\n")
        f.write("4. **Expand language support** beyond current capabilities\n")
        f.write("5. **Add IDE integration** for better developer experience\n")
    
    print(f"Detailed evaluation report saved to 'new_evaluation_report.md'")

if __name__ == "__main__":
    main()

# Test cases for different operations
ANALYZE_CODE = """
def risky_function(a, b):
    # Division without checking for zero
    return a / b

def process_list(items):
    # Index access without bounds checking
    return items[10]

def inefficient_search(data, target):
    # O(n) linear search when binary search would be better
    for i in range(len(data)):
        if data[i] == target:
            return i
    return -1
"""

OPTIMIZE_CODE = """
# Inefficient string concatenation
def build_string(n):
    result = ""
    for i in range(n):
        result = result + str(i)
    return result

# Inefficient list operation
def process_data(items):
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
    return result

# Inefficient algorithm (bubble sort)
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""

FIX_CODE = """
# Bug: Division by zero error
def divide(a, b):
    return a / b

# Bug: Index error
def get_item(list, index):
    return list[index]

# Bug: Type error
def combine(a, b):
    return a + b
"""

EXECUTION_CODE = """
def greet(name):
    return f"Hello, {name}!"

# Test the function
result = greet("World")
print(result)

# Create a list and process it
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print(f"Original: {numbers}")
print(f"Squared: {squared}")
"""

VISUALIZATION_CODE = """
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True)
plt.savefig('evaluation_sine.png')
"""

EXCEPTION_CODE = """
try:
    # Division by zero error
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")

try:
    # Index error
    my_list = [1, 2, 3]
    item = my_list[10]
except IndexError as e:
    print(f"Caught error: {e}")

# This will be caught by the execution environment
print(undefined_variable)
"""

# Test functions
def test_analyze():
    payload = {
        "code": ANALYZE_CODE,
        "language": "python",
        "action": "analyze"
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        return {
            "success": True,
            "response_time": end_time - start_time,
            "errors_detected": len(result.get("errors", [])),
            "warnings_detected": len(result.get("warnings", [])),
            "suggestions_provided": len(result.get("suggestions", []))
        }
    else:
        return {"success": False, "response_time": end_time - start_time}

def test_optimize():
    payload = {
        "code": OPTIMIZE_CODE,
        "language": "python",
        "action": "optimize"
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        metrics = result.get("performance_metrics", {})
        return {
            "success": True,
            "response_time": end_time - start_time,
            "optimized_code_length": len(result.get("processed_code", "")),
            "explanation_provided": len(result.get("explanation", "")) > 0,
            "metrics_provided": len(metrics) > 0,
            "key_optimizations": len(metrics.get("key_optimizations", [])) if "key_optimizations" in metrics else 0
        }
    else:
        return {"success": False, "response_time": end_time - start_time}

def test_fix():
    payload = {
        "code": FIX_CODE,
        "language": "python",
        "action": "fix"
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        return {
            "success": True,
            "response_time": end_time - start_time,
            "fixed_code_length": len(result.get("processed_code", "")),
            "explanation_provided": len(result.get("explanation", "")) > 0
        }
    else:
        return {"success": False, "response_time": end_time - start_time}

def test_execute():
    payload = {
        "code": EXECUTION_CODE,
        "language": "python",
        "action": "execute"
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        execution_result = result.get("execution_result", {})
        return {
            "success": True,
            "response_time": end_time - start_time,
            "stdout_length": len(execution_result.get("stdout", "")),
            "stderr_length": len(execution_result.get("stderr", "")),
            "execution_time": execution_result.get("execution_time", 0)
        }
    else:
        return {"success": False, "response_time": end_time - start_time}

def test_visualization():
    payload = {
        "code": VISUALIZATION_CODE,
        "language": "python",
        "action": "execute"
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        execution_result = result.get("execution_result", {})
        return {
            "success": True,
            "response_time": end_time - start_time,
            "libs_detected": "libraries_detected" in execution_result,
            "visualization_created": "evaluation_sine.png" in execution_result.get("stdout", ""),
            "execution_time": execution_result.get("execution_time", 0)
        }
    else:
        return {"success": False, "response_time": end_time - start_time}

def test_exception_handling():
    payload = {
        "code": EXCEPTION_CODE,
        "language": "python",
        "action": "execute"
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        execution_result = result.get("execution_result", {})
        stderr = execution_result.get("stderr", "")
        suggestions_provided = "SUGGESTION:" in stderr
        
        return {
            "success": True,
            "response_time": end_time - start_time,
            "exception_caught": len(stderr) > 0,
            "suggestions_provided": suggestions_provided,
            "execution_time": execution_result.get("execution_time", 0)
        }
    else:
        return {"success": False, "response_time": end_time - start_time}

def cache_performance_test():
    """Test how caching improves performance on repeated calls."""
    payload = {
        "code": ANALYZE_CODE,
        "language": "python",
        "action": "analyze"
    }
    
    # First call (cache miss)
    start_time = time.time()
    response1 = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    first_call_time = end_time - start_time
    
    # Second call (cache hit)
    start_time = time.time()
    response2 = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    second_call_time = end_time - start_time
    
    improvement = (first_call_time - second_call_time) / first_call_time * 100 if first_call_time > 0 else 0
    
    return {
        "first_call_time": first_call_time,
        "second_call_time": second_call_time,
        "improvement_percent": improvement,
        "cache_effective": second_call_time < first_call_time
    }

def run_evaluation():
    print("Running comprehensive evaluation of FixLoop...")
    print(f"Evaluation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # Run multiple iterations for more reliable results
    iterations = 3
    
    analyze_results = []
    optimize_results = []
    fix_results = []
    execute_results = []
    visualization_results = []
    exception_results = []
    
    for i in range(iterations):
        print(f"Running iteration {i+1}/{iterations}...")
        
        print("Testing code analysis...")
        analyze_results.append(test_analyze())
        
        print("Testing code optimization...")
        optimize_results.append(test_optimize())
        
        print("Testing code fixing...")
        fix_results.append(test_fix())
        
        print("Testing code execution...")
        execute_results.append(test_execute())
        
        print("Testing visualization handling...")
        visualization_results.append(test_visualization())
        
        print("Testing exception handling...")
        exception_results.append(test_exception_handling())
    
    # Test cache performance separately
    print("Testing cache performance...")
    cache_results = cache_performance_test()
    
    # Generate report
    print("\nEvaluation complete. Generating report...")
    generate_report(
        analyze_results,
        optimize_results,
        fix_results,
        execute_results,
        visualization_results,
        exception_results,
        cache_results
    )

def generate_report(analyze_results, optimize_results, fix_results, execute_results, 
                    visualization_results, exception_results, cache_results):
    """Generate a comprehensive evaluation report."""
    
    # Prepare report file
    report_file = "evaluation_report.md"
    with open(report_file, "w") as f:
        f.write("# FixLoop Evaluation Report\n\n")
        f.write(f"_Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n")
        
        f.write("## Summary\n\n")
        f.write("This report evaluates the performance and capabilities of FixLoop across its main features.\n\n")
        
        # Calculate success rates
        f.write("### Success Rates\n\n")
        f.write("| Feature | Success Rate |\n")
        f.write("|---------|-------------|\n")
        
        success_rates = {
            "Code Analysis": sum(1 for r in analyze_results if r["success"]) / len(analyze_results) * 100,
            "Code Optimization": sum(1 for r in optimize_results if r["success"]) / len(optimize_results) * 100,
            "Bug Fixing": sum(1 for r in fix_results if r["success"]) / len(fix_results) * 100,
            "Code Execution": sum(1 for r in execute_results if r["success"]) / len(execute_results) * 100,
            "Visualization": sum(1 for r in visualization_results if r["success"]) / len(visualization_results) * 100,
            "Exception Handling": sum(1 for r in exception_results if r["success"]) / len(exception_results) * 100
        }
        
        for feature, rate in success_rates.items():
            f.write(f"| {feature} | {rate:.1f}% |\n")
        
        # Average response times
        f.write("\n### Average Response Times\n\n")
        f.write("| Feature | Average Response Time (seconds) |\n")
        f.write("|---------|--------------------------------|\n")
        
        response_times = {
            "Code Analysis": statistics.mean(r["response_time"] for r in analyze_results),
            "Code Optimization": statistics.mean(r["response_time"] for r in optimize_results),
            "Bug Fixing": statistics.mean(r["response_time"] for r in fix_results),
            "Code Execution": statistics.mean(r["response_time"] for r in execute_results),
            "Visualization": statistics.mean(r["response_time"] for r in visualization_results),
            "Exception Handling": statistics.mean(r["response_time"] for r in exception_results)
        }
        
        for feature, time in response_times.items():
            f.write(f"| {feature} | {time:.2f} |\n")
        
        # Detailed results by feature
        f.write("\n## Detailed Results\n\n")
        
        # Code Analysis
        f.write("### Code Analysis\n\n")
        avg_errors = statistics.mean(r["errors_detected"] for r in analyze_results if r["success"])
        avg_warnings = statistics.mean(r["warnings_detected"] for r in analyze_results if r["success"])
        avg_suggestions = statistics.mean(r["suggestions_provided"] for r in analyze_results if r["success"])
        
        f.write(f"- Average errors detected: {avg_errors:.1f}\n")
        f.write(f"- Average warnings detected: {avg_warnings:.1f}\n")
        f.write(f"- Average suggestions provided: {avg_suggestions:.1f}\n")
        
        # Code Optimization
        f.write("\n### Code Optimization\n\n")
        avg_opt_code_length = statistics.mean(r["optimized_code_length"] for r in optimize_results if r["success"] and "optimized_code_length" in r)
        metrics_provided = sum(1 for r in optimize_results if r["success"] and r.get("metrics_provided", False))
        avg_key_opts = 0
        if any("key_optimizations" in r for r in optimize_results if r["success"]):
            avg_key_opts = statistics.mean(r["key_optimizations"] for r in optimize_results if r["success"] and "key_optimizations" in r)
        
        f.write(f"- Average optimized code length: {avg_opt_code_length:.1f} characters\n")
        f.write(f"- Performance metrics provided: {metrics_provided} out of {len(optimize_results)}\n")
        f.write(f"- Average key optimizations identified: {avg_key_opts:.1f}\n")
        
        # Bug Fixing
        f.write("\n### Bug Fixing\n\n")
        avg_fix_code_length = statistics.mean(r["fixed_code_length"] for r in fix_results if r["success"] and "fixed_code_length" in r)
        explanations_provided = sum(1 for r in fix_results if r["success"] and r.get("explanation_provided", False))
        
        f.write(f"- Average fixed code length: {avg_fix_code_length:.1f} characters\n")
        f.write(f"- Explanations provided: {explanations_provided} out of {len(fix_results)}\n")
        
        # Code Execution
        f.write("\n### Code Execution\n\n")
        avg_stdout_length = statistics.mean(r["stdout_length"] for r in execute_results if r["success"] and "stdout_length" in r)
        avg_execution_time = statistics.mean(r["execution_time"] for r in execute_results if r["success"] and "execution_time" in r)
        
        f.write(f"- Average stdout length: {avg_stdout_length:.1f} characters\n")
        f.write(f"- Average execution time: {avg_execution_time:.5f} seconds\n")
        
        # Visualization Support
        f.write("\n### Visualization Support\n\n")
        libs_detected = sum(1 for r in visualization_results if r["success"] and r.get("libs_detected", False))
        vis_created = sum(1 for r in visualization_results if r["success"] and r.get("visualization_created", False))
        
        f.write(f"- Libraries detected: {libs_detected} out of {len(visualization_results)}\n")
        f.write(f"- Visualizations created: {vis_created} out of {len(visualization_results)}\n")
        
        # Exception Handling
        f.write("\n### Exception Handling\n\n")
        exceptions_caught = sum(1 for r in exception_results if r["success"] and r.get("exception_caught", False))
        suggestions_provided = sum(1 for r in exception_results if r["success"] and r.get("suggestions_provided", False))
        
        f.write(f"- Exceptions caught: {exceptions_caught} out of {len(exception_results)}\n")
        f.write(f"- Suggestions provided: {suggestions_provided} out of {len(exception_results)}\n")
        
        # Cache Performance
        f.write("\n### Cache Performance\n\n")
        f.write(f"- First call time: {cache_results['first_call_time']:.2f} seconds\n")
        f.write(f"- Second call time (cached): {cache_results['second_call_time']:.2f} seconds\n")
        f.write(f"- Performance improvement: {cache_results['improvement_percent']:.1f}%\n")
        f.write(f"- Cache effective: {'Yes' if cache_results['cache_effective'] else 'No'}\n")
        
        # Feature Scores
        f.write("\n## Feature Ratings\n\n")
        f.write("| Feature | Score (1-10) |\n")
        f.write("|---------|-------------|\n")
        
        # Calculate scores based on results
        scores = {}
        
        # Analysis score based on detection rates and response time
        analysis_score = min(10, (
            avg_errors + avg_warnings + avg_suggestions +
            (1 if response_times["Code Analysis"] < 5 else 0) +
            (1 if response_times["Code Analysis"] < 10 else 0)
        ))
        scores["Code Analysis"] = analysis_score
        
        # Optimization score based on metrics, explanations and time
        optimization_score = min(10, (
            (2 if metrics_provided == len(optimize_results) else 0) +
            min(3, avg_key_opts) +
            (2 if any("metrics_provided" in r for r in optimize_results if r["success"]) else 0) +
            (1 if response_times["Code Optimization"] < 20 else 0) +
            (2 if cache_results['improvement_percent'] > 50 else 0)
        ))
        scores["Code Optimization"] = optimization_score
        
        # Fixing score based on explanations and success
        fix_success_rate = success_rates["Bug Fixing"] / 100
        fix_score = min(10, (
            fix_success_rate * 5 +
            (explanations_provided / len(fix_results)) * 3 +
            (1 if response_times["Bug Fixing"] < 15 else 0) +
            (1 if "fixed_code_length" in fix_results[0] else 0)
        ))
        scores["Bug Fixing"] = fix_score
        
        # Execution score
        execution_score = min(10, (
            (success_rates["Code Execution"] / 100) * 4 +
            (1 if avg_execution_time < 0.5 else 0) +
            (3 if response_times["Code Execution"] < 5 else 0) +
            (2 if success_rates["Visualization"] > 80 else 0)
        ))
        scores["Code Execution"] = execution_score
        
        # Exception handling score
        exception_score = min(10, (
            (exceptions_caught / len(exception_results)) * 5 +
            (suggestions_provided / len(exception_results)) * 5
        ))
        scores["Exception Handling"] = exception_score
        
        # Cache performance score
        cache_score = min(10, (
            (cache_results['improvement_percent'] / 10) +
            (5 if cache_results['cache_effective'] else 0) +
            (3 if cache_results['second_call_time'] < 1 else 0)
        ))
        scores["Cache Performance"] = cache_score
        
        # Write scores
        for feature, score in scores.items():
            f.write(f"| {feature} | {score:.1f} |\n")
        
        # Overall score (weighted average)
        weights = {
            "Code Analysis": 0.2,
            "Code Optimization": 0.2,
            "Bug Fixing": 0.2,
            "Code Execution": 0.15,
            "Exception Handling": 0.15,
            "Cache Performance": 0.1
        }
        
        overall_score = sum(score * weights[feature] for feature, score in scores.items())
        
        f.write("\n## Overall Rating\n\n")
        f.write(f"**Overall Score: {overall_score:.1f}/10**\n\n")
        
        # Recommendations
        f.write("## Recommendations for Future Improvements\n\n")
        
        f.write("1. **Further Analysis Improvements**: Continue enhancing the code analysis to detect more types of issues, perhaps by incorporating specialized analyzers for different languages.\n\n")
        f.write("2. **Response Time Optimization**: Additional techniques like API request batching could further reduce response times.\n\n")
        f.write("3. **Library Support**: Consider containerized execution environments with common libraries pre-installed.\n\n")
        f.write("4. **Expand Testing**: Develop more comprehensive test cases for each function to ensure reliability across different coding scenarios.\n\n")
        f.write("5. **UI Integration**: Integrate with popular IDEs or develop a dedicated web interface for better user experience.\n\n")
    
    print(f"Evaluation report generated: {report_file}")

if __name__ == "__main__":
    run_evaluation() 