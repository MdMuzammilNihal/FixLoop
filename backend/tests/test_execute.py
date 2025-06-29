import requests
import time
import json

def test_execute():
    code = """
print("Hello, World!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""

    payload = {
        "code": code,
        "language": "python",
        "action": "execute"
    }
    
    print("Testing execution functionality with simple Python code...")
    start_time = time.time()
    
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nOriginal code:")
        print(code)
        
        print("\nExecution result:")
        if "execution_result" in result:
            # Pretty print the execution result
            execution_result = result["execution_result"]
            if isinstance(execution_result, str):
                try:
                    # Try to parse as JSON in case it's a JSON string
                    parsed_result = json.loads(execution_result)
                    print(json.dumps(parsed_result, indent=2))
                except:
                    # Just print as is if not valid JSON
                    print(execution_result)
            else:
                print(json.dumps(execution_result, indent=2))
        else:
            print("No execution result provided")
    else:
        print(f"Error: {response.text}")

def test_execute_with_input():
    code = """
name = input("What is your name? ")
age = input("How old are you? ")
print(f"Hello {name}, you are {age} years old!")

# Calculate birth year
current_year = 2024
birth_year = current_year - int(age)
print(f"You were born around {birth_year}.")
"""

    payload = {
        "code": code,
        "language": "python",
        "action": "execute",
        "inputs": ["Alice", "30"]
    }
    
    print("\nTesting execution functionality with user input...")
    start_time = time.time()
    
    response = requests.post("http://localhost:8000/api/code", json=payload)
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nOriginal code:")
        print(code)
        
        print("\nInputs provided:")
        print(payload["inputs"])
        
        print("\nExecution result:")
        if "execution_result" in result:
            # Pretty print the execution result
            execution_result = result["execution_result"]
            if isinstance(execution_result, str):
                try:
                    # Try to parse as JSON in case it's a JSON string
                    parsed_result = json.loads(execution_result)
                    print(json.dumps(parsed_result, indent=2))
                except:
                    # Just print as is if not valid JSON
                    print(execution_result)
            else:
                print(json.dumps(execution_result, indent=2))
        else:
            print("No execution result provided")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_execute()
    test_execute_with_input() 