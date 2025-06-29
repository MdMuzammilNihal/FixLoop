import requests
import time

def test_fix():
    code = """
def add(a, b):
    return a - b  # Bug: should be a + b
"""

    payload = {
        "code": code,
        "language": "python",
        "action": "fix"
    }
    
    print("Testing fix functionality with a simple bug...")
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
    test_fix() 