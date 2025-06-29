import httpx
import asyncio
import json

async def check_models():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("Response data:")
                print(json.dumps(data, indent=2))
                
                if "models" in data:
                    print("\nAvailable models:")
                    for model in data["models"]:
                        print(f"- {model.get('name')}")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(check_models()) 