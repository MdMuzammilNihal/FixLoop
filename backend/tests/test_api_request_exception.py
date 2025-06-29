import requests
import json

def test_exception_handling():
    # Code with various errors to test exception handling
    code = """
# Import error
import matplotlib.pyplot as plt

# Division by zero error
def divide(a, b):
    return a / b

result = divide(10, 0)

# Index error
my_list = [1, 2, 3]
item = my_list[10]

# Try to access undefined variable
print(undefined_variable)
"""

    # Prepare the API request
    payload = {
        "code": code,
        "language": "python",
        "action": "execute"
    }
    
    # Make the API request
    print("Testing enhanced exception handling...")
    response = requests.post("http://localhost:8000/api/code", json=payload)
    
    # Print the results
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        result = json.loads(response.text)
        print("\nOriginal code:")
        print(code)
        
        print("\nExecution result:")
        if "execution_result" in result:
            execution_result = result["execution_result"]
            if isinstance(execution_result, str):
                print(execution_result)
            else:
                # Check for stderr with enhanced error messages
                if execution_result.get("stderr"):
                    print("Error output:")
                    print(execution_result["stderr"])
                
                # Check for enhanced suggestions
                if "SUGGESTION:" in execution_result.get("stderr", ""):
                    print("\nProvided suggestions:")
                    stderr = execution_result["stderr"]
                    suggestions = [line.strip() for line in stderr.split("\n") if "SUGGESTION:" in line]
                    for suggestion in suggestions:
                        print(f"- {suggestion}")
        else:
            print("No execution result provided")
    else:
        print(f"Error: {response.text}")

def test_visualization_handling():
    # Code that uses visualization libraries
    code = """
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

# No plt.show() or plt.savefig() - test auto-detection
"""

    # Prepare the API request
    payload = {
        "code": code,
        "language": "python",
        "action": "execute"
    }
    
    # Make the API request
    print("\nTesting visualization library detection...")
    response = requests.post("http://localhost:8000/api/code", json=payload)
    
    # Print the results
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        result = json.loads(response.text)
        
        print("\nExecution result:")
        if "execution_result" in result:
            execution_result = result["execution_result"]
            if isinstance(execution_result, str):
                print(execution_result)
            else:
                # Check for library detection
                if "libraries_detected" in execution_result:
                    print("\nDetected libraries:")
                    for lib in execution_result["libraries_detected"]:
                        print(f"- {lib}")
                
                # Check for visualization suggestions
                if execution_result.get("stdout"):
                    print("\nOutput:")
                    print(execution_result["stdout"])
        else:
            print("No execution result provided")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_exception_handling()
    test_visualization_handling() 