#!/usr/bin/env python3
"""
FixLoop - Ollama Test Script

This script checks if Ollama is properly installed and available for use with FixLoop.
"""

import os
import sys
import time
import httpx
import json
from typing import List, Dict, Any, Tuple
import platform
import psutil

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
REQUIRED_MODELS = ["llama3"]

def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60)

def print_result(success: bool, message: str) -> None:
    """Print a formatted result."""
    icon = "✓" if success else "✗"
    print(f"\n{icon} {message}")

async def check_ollama_connection() -> Tuple[bool, List[str]]:
    """Check if Ollama is running and get available models."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = [model.get("name") for model in response.json().get("models", [])]
                return True, models
            return False, []
    except Exception as e:
        return False, []

async def test_model_generation(model: str, prompt: str = "Hello, how are you?") -> Tuple[bool, float, str]:
    """Test generating text with the specified model."""
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            
            if response.status_code != 200:
                return False, 0, f"API error: {response.status_code}"
                
            generation_time = time.time() - start_time
            result = response.json().get("response", "")
            return True, generation_time, result[:100] + "..." if len(result) > 100 else result
    except httpx.TimeoutException:
        return False, 0, "Request timed out"
    except Exception as e:
        return False, 0, f"Error: {str(e)}"

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "memory_total": round(psutil.virtual_memory().total / (1024**3), 2),  # GB
        "memory_available": round(psutil.virtual_memory().available / (1024**3), 2),  # GB
        "disk_free": round(psutil.disk_usage('/').free / (1024**3), 2),  # GB
    }

def print_system_info(info: Dict[str, Any]) -> None:
    """Print system information in a formatted way."""
    print("\nSystem Information:")
    print(f"  Operating System: {info['os']} {info['os_version']}")
    print(f"  Architecture: {info['architecture']}")
    print(f"  Python Version: {info['python_version']}")
    print(f"  CPU Cores: {info['physical_cpu_count']} physical, {info['cpu_count']} logical")
    print(f"  Memory: {info['memory_available']} GB available / {info['memory_total']} GB total")
    print(f"  Disk Space: {info['disk_free']} GB free")

async def run_tests() -> None:
    """Run all tests."""
    print_header("FixLoop - Ollama Test Script")
    
    # Check system requirements
    system_info = get_system_info()
    print_system_info(system_info)
    
    # Check for minimum system requirements
    has_minimum_resources = (
        system_info["memory_total"] >= 8 and  # At least 8GB RAM
        system_info["disk_free"] >= 10  # At least 10GB free disk space
    )
    print_result(has_minimum_resources, 
                "System meets minimum requirements" if has_minimum_resources else 
                "System does not meet minimum requirements (need: 8GB RAM, 10GB disk space)")
    
    # Check Ollama connection
    print("\nChecking Ollama connection...")
    ollama_available, available_models = await check_ollama_connection()
    print_result(ollama_available, 
                f"Ollama is available at {OLLAMA_BASE_URL}" if ollama_available else 
                f"Ollama is not available at {OLLAMA_BASE_URL}")
    
    if ollama_available:
        print("\nAvailable models:", ", ".join(available_models) if available_models else "None")
        
        # Check for required models
        missing_models = [model for model in REQUIRED_MODELS if model not in available_models]
        if missing_models:
            print("\nMissing required models:", ", ".join(missing_models))
            print("\nPlease install the missing models with:")
            for model in missing_models:
                print(f"  ollama pull {model}")
        else:
            print_result(True, "All required models are available")
            
            # Test model generation
            print("\nTesting model generation...")
            for model in REQUIRED_MODELS:
                if model in available_models:
                    success, gen_time, result = await test_model_generation(model)
                    print_result(success, 
                                f"Model '{model}' generated text in {gen_time:.2f}s" if success else 
                                f"Failed to generate text with model '{model}'")
                    if success:
                        print(f"  Sample output: {result}")
    
    # Summary
    print_header("Test Summary")
    if not ollama_available:
        print("Ollama is not available. Please install and start Ollama.")
        print("See docs/OLLAMA_SETUP.md for installation instructions.")
    elif missing_models:
        print("Ollama is running, but some required models are missing.")
        print("Install the missing models and run this test again.")
    else:
        print("All tests passed! FixLoop should work correctly with Ollama.")
        print("Start it with: python -m uvicorn backend.main:app --port 8000")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests()) 