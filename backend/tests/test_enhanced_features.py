"""
Test script for enhanced FixLoop features
"""
import requests
import json
import time
import sys
import os

# Define the API endpoint
API_URL = "http://localhost:8000"

def test_visualization_detection():
    """Test enhanced visualization library detection and saving."""
    print("Testing enhanced visualization library detection...")
    
    code = """
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'r-', label='Sine wave')
plt.title('Enhanced Visualization Test')
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.legend()
plt.grid(True)
plt.show()
"""
    
    response = requests.post(
        f"{API_URL}/api/code",
        json={
            "code": code,
            "language": "python",
            "action": "execute"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if "libraries_detected" in result and "matplotlib" in result.get("libraries_detected", []):
            print("✅ Successfully detected matplotlib library")
        else:
            print("❌ Failed to detect matplotlib library")
            
        # Check for visualization saving suggestions
        if "stdout" in result and "[INFO] Saving" in result.get("stdout", ""):
            print("✅ Successfully generated plot saving code")
        else:
            print("❌ Failed to generate plot saving code")
    else:
        print(f"❌ API request failed with status code {response.status_code}")
        print(response.text)
        
def test_enhanced_error_handling():
    """Test enhanced error handling with detailed suggestions."""
    print("\nTesting enhanced error handling...")
    
    code = """
def process_data(data):
    result = []
    for i in range(len(data)):
        # Potential index error
        next_val = data[i+1]  
        result.append(data[i] + next_val)
    return result

sample_data = [1, 2, 3, 4, 5]
print(process_data(sample_data))
"""
    
    response = requests.post(
        f"{API_URL}/api/code",
        json={
            "code": code,
            "language": "python",
            "action": "execute"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        error_output = result.get("execution_result", {}).get("stderr", "")
        
        if "IndexError" in error_output:
            print("✅ Correctly identified IndexError")
            
            if "SUGGESTION" in error_output and "list index out of range" in error_output:
                print("✅ Provided enhanced error suggestion")
                if "Example fix" in error_output or "```python" in error_output:
                    print("✅ Included code example in suggestion")
                else:
                    print("❌ Missing code example in suggestion")
            else:
                print("❌ Missing enhanced error suggestion")
        else:
            print("❓ No IndexError was detected, test inconclusive")
    else:
        print(f"❌ API request failed with status code {response.status_code}")
        
def test_optimization_metrics():
    """Test enhanced optimization metrics."""
    print("\nTesting enhanced optimization metrics...")
    
    code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
        
print(fibonacci(10))
"""
    
    response = requests.post(
        f"{API_URL}/api/code",
        json={
            "code": code,
            "language": "python",
            "action": "optimize"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        metrics = result.get("performance_metrics", {})
        
        if metrics:
            print("✅ Generated performance metrics")
            
            if "time_complexity" in metrics:
                print("✅ Included time complexity metrics")
                if "improvement_analysis" in metrics:
                    print("✅ Included detailed complexity improvement analysis")
                else:
                    print("❌ Missing detailed complexity improvement analysis")
            else:
                print("❌ Missing time complexity metrics")
                
            if "language_specific_insights" in metrics:
                print("✅ Included language-specific optimization insights")
            else:
                print("❌ Missing language-specific optimization insights")
                
            if "optimizations" in metrics or "key_optimizations" in metrics:
                print("✅ Included categorized optimizations")
            else:
                print("❌ Missing categorized optimizations")
        else:
            print("❌ Missing performance metrics")
    else:
        print(f"❌ API request failed with status code {response.status_code}")
        
def test_context_aware_fix():
    """Test the new context-aware fix API endpoint."""
    print("\nTesting context-aware fix API...")
    
    code = """
def connect_to_database(config):
    conn = DatabaseConnection(
        host=config['host'],
        port=config['port'],
        username=config['username'],
        password=config['password']
    )
    return conn
"""
    
    # Provide context information
    error_message = "TypeError: 'NoneType' object is not subscriptable at line 3"
    context = "DatabaseConnection is a custom class that requires database configuration. The config parameter might be None."
    dependencies = ["custom_db_library>=1.2.0"]
    
    response = requests.post(
        f"{API_URL}/api/code/fix-with-context",
        json={
            "code": code,
            "language": "python",
            "error_message": error_message,
            "context": context,
            "dependencies": dependencies
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if "fixed_code" in result and result["fixed_code"] != code:
            print("✅ Generated fixed code with context")
            
            if "bugs_found" in result and result["bugs_found"]:
                print("✅ Identified specific bugs")
            else:
                print("❌ Failed to identify specific bugs")
                
            if "context_info" in result:
                print("✅ Included context information in response")
                if "error_line" in result["context_info"]:
                    print("✅ Extracted line number from error message")
                else:
                    print("❌ Failed to extract line number from error message")
            else:
                print("❌ Missing context information in response")
        else:
            print("❌ Failed to generate context-aware fix")
    else:
        print(f"❌ API request failed with status code {response.status_code}")
        if response.text:
            print(response.text)

if __name__ == "__main__":
    # Check if the API is running
    try:
        health_response = requests.get(f"{API_URL}/api/health")
        if health_response.status_code != 200 or not health_response.json().get("ollama_available"):
            print("❌ API is not running or Ollama is not available. Please start the API first.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Could not connect to API: {str(e)}")
        print("Make sure FixLoop is running at http://localhost:8000")
        sys.exit(1)
    
    print("🧪 Starting enhanced features tests for FixLoop...\n")
    
    # Run tests
    test_visualization_detection()
    test_enhanced_error_handling()
    test_optimization_metrics()
    test_context_aware_fix()
    
    print("\n🏁 All tests completed!") 