import requests
import json

API_URL = "http://localhost:8000/api"

def test_simple_execution():
    """Test basic execution functionality"""
    code = "print('Hello, World!')"
    
    response = requests.post(
        f"{API_URL}/code",
        json={"code": code, "language": "python", "action": "execute"}
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nResults:")
        if "execution_result" in data:
            print(f"Exit code: {data['execution_result'].get('exit_code', 'N/A')}")
            print(f"Output: {data['execution_result'].get('stdout', '')}")
            if data['execution_result'].get('stderr'):
                print(f"Error: {data['execution_result'].get('stderr', '')}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_simple_execution() 