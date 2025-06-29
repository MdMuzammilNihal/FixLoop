import requests
import json

API_URL = "http://localhost:8000/api"

def test_execution():
    """Test the execution endpoint with a simple code example"""
    print("Testing code execution...")
    
    code = """
print("Hello, World!")
    """
    
    response = requests.post(
        f"{API_URL}/code",
        json={"code": code, "language": "python", "action": "execute"}
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nExecution Results:")
        if "execution_result" in data and "stdout" in data["execution_result"]:
            print(f"Output: {data['execution_result']['stdout']}")
        else:
            print("No execution output found in response")
        print("\nFull response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_execution() 