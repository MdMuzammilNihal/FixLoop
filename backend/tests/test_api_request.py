import requests
import json

def test_fix_api():
    # Code with a bug to fix
    code = """
def sum_numbers(n):
    total = 0
    for i in range(0, n - 1):  # Bug: should be range(0, n) or range(n)
        total += i
    return total
"""

    # Prepare the API request
    payload = {
        "code": code,
        "language": "python",
        "action": "fix"
    }
    
    # Make the API request
    response = requests.post("http://localhost:8000/api/code", json=payload)
    
    # Print the results
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        result = json.loads(response.text)
        print("\nOriginal code:")
        print(code)
        
        print("\nFixed code:")
        if "processed_code" in result:
            print(result["processed_code"])
        else:
            print("No processed code provided")
            
        print("\nExplanation:")
        if "explanation" in result:
            print(result["explanation"])
        else:
            print("No explanation provided")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_fix_api() 