import requests
import json
import time

def test_optimization_with_metrics():
    # Inefficient code example with various optimization opportunities
    code = """
# Inefficient string concatenation in a loop
def build_string(n):
    result = ""
    for i in range(n):
        result = result + str(i)
    return result

# Inefficient list building
def create_squared_list(n):
    squares = []
    for i in range(n):
        squares.append(i * i)
    return squares

# Inefficient searching algorithm (linear search)
def find_element(array, target):
    for i in range(len(array)):
        if array[i] == target:
            return i
    return -1

# Inefficient data processing with nested loops
def process_matrix(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    result = []
    for i in range(rows):
        row_sum = 0
        for j in range(cols):
            row_sum += matrix[i][j]
        result.append(row_sum)
    return result
"""

    # Prepare the API request
    payload = {
        "code": code,
        "language": "python",
        "action": "optimize"
    }
    
    # Make the API request
    print("Testing enhanced optimization with performance metrics...")
    start_time = time.time()
    
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    # Print the results
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = json.loads(response.text)
        print("\nOriginal code:")
        print(code)
        
        print("\nOptimized code:")
        if "processed_code" in result:
            print(result["processed_code"])
        else:
            print("No optimized code provided")
            
        print("\nPerformance metrics:")
        if "performance_metrics" in result:
            metrics = result["performance_metrics"]
            
            if "summary" in metrics:
                print(f"Summary: {metrics['summary']}")
                
            if "impact" in metrics:
                print(f"Impact: {metrics['impact']}")
                
            if "time_complexity" in metrics:
                print(f"Time complexity improvement: {metrics['time_complexity']['before']} → {metrics['time_complexity']['after']}")
                
            if "memory_improvement" in metrics:
                print(f"Memory improvement: {metrics['memory_improvement']}")
                
            if "key_optimizations" in metrics:
                print("\nKey optimizations:")
                for i, opt in enumerate(metrics["key_optimizations"]):
                    print(f"{i+1}. {opt}")
        else:
            print("No performance metrics provided")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_optimization_with_metrics() 