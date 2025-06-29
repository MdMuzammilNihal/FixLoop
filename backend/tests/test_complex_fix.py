import requests
import time

def test_complex_fix():
    code = """
def find_median(numbers):
    # Bug 1: No sorting before finding median
    # Bug 2: Wrong indexing
    # Bug 3: No handling for even length lists
    n = len(numbers)
    return numbers[n // 2]

def binary_search(arr, target):
    # Bug 1: Not handling empty array
    # Bug 2: Wrong comparison (should be arr[mid] == target)
    # Bug 3: Infinite loop potential (incorrect update of low/high)
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] < target:
            low = mid
        else:
            high = mid
    
    return -1  # Not found
"""

    payload = {
        "code": code,
        "language": "python",
        "action": "fix"
    }
    
    print("Testing fix functionality with complex bugs...")
    start_time = time.time()
    
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nOriginal code:")
        print(code)
        
        print("\nFixed code:")
        print(result.get("processed_code", "No fixed code provided"))
        
        print("\nExplanation:")
        print(result.get("explanation", "No explanation provided"))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_complex_fix() 