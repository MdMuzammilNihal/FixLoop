import requests
import time
import json

def test_optimize():
    # Read the test optimization code
    with open("test_optimization.py", "r") as f:
        code = f.read()

    payload = {
        "code": code,
        "language": "python",
        "action": "optimize"
    }
    
    print("Testing optimization functionality with inefficient code...")
    start_time = time.time()
    
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\nExplanation:")
        explanation = result.get("explanation", "No explanation provided")
        print(explanation[:500] + "..." if len(explanation) > 500 else explanation)
        
        print("\nOptimized code:")
        optimized_code = result.get("processed_code", "No optimized code provided")
        
        # Print a snippet of the optimized code
        code_lines = optimized_code.split("\n")
        for i, line in enumerate(code_lines[:100]):  # Show more lines for better context
            print(f"{i+1}: {line}")
        if len(code_lines) > 100:
            print("...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_optimize() 