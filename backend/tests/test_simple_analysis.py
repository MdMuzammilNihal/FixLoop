import requests
import time

def test_simple_analysis():
    code = """
def divide(a, b):
    return a / b  # No division by zero check
"""

    payload = {
        "code": code,
        "language": "python",
        "action": "analyze"
    }
    
    print("Testing analysis with simple code...")
    start_time = time.time()
    
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\nErrors:")
        for error in result.get("errors", []):
            print(f"- {error}")
        
        print("\nWarnings:")
        for warning in result.get("warnings", []):
            print(f"- {warning}")
        
        print("\nSuggestions:")
        for suggestion in result.get("suggestions", []):
            print(f"- {suggestion}")
            
        if not result.get("errors") and not result.get("warnings") and not result.get("suggestions"):
            print("\nRaw analysis:")
            print(result.get("analysis", "No analysis provided")[:500] + "..." if len(result.get("analysis", "")) > 500 else result.get("analysis", ""))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_simple_analysis() 