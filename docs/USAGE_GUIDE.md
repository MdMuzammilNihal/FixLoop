# FixLoop Usage Guide

## Table of Contents
- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
  - [Code Analysis](#code-analysis)
  - [Bug Fixing](#bug-fixing)
  - [Code Optimization](#code-optimization)
  - [Code Execution](#code-execution)
  - [Data Visualization](#data-visualization)
  - [Machine Learning Support](#machine-learning-support)
  - [Exception Handling](#exception-handling)
  - [API Integration](#api-integration)
- [IDE Integration](#ide-integration)
- [Configuration](#configuration)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Introduction

FixLoop is a free, research-grade self-correcting AI coding assistant designed to help developers with various coding tasks. It combines advanced code analysis, bug fixing, optimization, and execution capabilities in a single tool.

## Getting Started

FixLoop can be used via its API endpoints or through the web interface. The typical workflow is:

1. Submit your code for analysis
2. Receive suggestions, optimizations, or fixes
3. Apply the changes and/or execute the code
4. Iterate as needed

## Key Features

- **Code Analysis**: Detailed analysis with errors, warnings, and style suggestions
- **Bug Fixing**: Automated identification and correction of common coding errors
- **Code Optimization**: Performance improvements and algorithmically optimized code
- **Code Execution**: Safe execution environment with input/output handling
- **Data Visualization**: Support for matplotlib, pandas, and other visualization libraries
- **Machine Learning Support**: Integration with scikit-learn, TensorFlow, and other ML frameworks
- **Exception Handling**: Robust error detection and handling
- **API Integration**: Support for making and handling API requests

## Installation

### Prerequisites
- Python 3.8+
- Docker (optional, for containerized deployment)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fixloop.git
   cd fixloop
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (optional):
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

4. Start the server:
   ```bash
   python fixloop.py
   ```

Alternatively, you can use Docker:

```bash
docker-compose up -d
```

## Usage

### Code Analysis

To analyze your code for potential issues:

```python
import requests

code = """
def sum_numbers(a, b)
    return a + b
"""

response = requests.post("http://localhost:8000/api/code", json={
    "code": code,
    "language": "python",
    "action": "analyze"
})

print(response.json())
```

Example response:
```json
{
  "original_code": "def sum_numbers(a, b)\n    return a + b",
  "explanation": "Your code has a syntax error: missing colon after function parameters.",
  "errors": ["SyntaxError: Missing colon after function parameters"],
  "processing_time": 0.234
}
```

### Bug Fixing

To fix bugs in your code:

```python
import requests

code = """
def divide(a, b):
    return a / b
    
result = divide(10, 0)
print(result)
"""

response = requests.post("http://localhost:8000/api/code", json={
    "code": code,
    "language": "python",
    "action": "fix"
})

print(response.json())
```

Example response:
```json
{
  "original_code": "def divide(a, b):\n    return a / b\n    \nresult = divide(10, 0)\nprint(result)",
  "processed_code": "def divide(a, b):\n    if b == 0:\n        return 'Cannot divide by zero'\n    return a / b\n    \nresult = divide(10, 0)\nprint(result)",
  "explanation": "Added a check to prevent division by zero.",
  "processing_time": 0.312
}
```

### Code Optimization

To optimize your code for better performance:

```python
import requests

code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
        
print(fibonacci(30))
"""

response = requests.post("http://localhost:8000/api/code", json={
    "code": code,
    "language": "python",
    "action": "optimize"
})

print(response.json())
```

Example response shows a memoization-based optimization.

### Code Execution

To execute your code with inputs:

```python
import requests

code = """
def greet(name):
    return f"Hello, {name}!"
    
name = input("Enter your name: ")
print(greet(name))
"""

response = requests.post("http://localhost:8000/api/code", json={
    "code": code,
    "language": "python",
    "action": "execute",
    "inputs": ["John"]
})

print(response.json())
```

Example response includes execution results.

### Data Visualization

FixLoop supports various data visualization libraries including matplotlib and pandas:

```python
import requests

code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title('Sine Wave')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.show()
"""

response = requests.post("http://localhost:8000/api/code", json={
    "code": code,
    "language": "python",
    "action": "execute"
})

print(response.json())
```

The response will include information about the generated visualization.

### Machine Learning Support

FixLoop supports machine learning code execution and optimization:

```python
import requests

code = """
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy:.4f}")
"""

response = requests.post("http://localhost:8000/api/code", json={
    "code": code,
    "language": "python",
    "action": "execute"
})

print(response.json())
```

## IDE Integration

### VS Code Extension

FixLoop can be integrated with Visual Studio Code using the FixLoop extension:

1. Install the extension from the VS Code marketplace
2. Configure the extension with your FixLoop server URL
3. Use the extension commands to analyze, fix, or optimize your code directly in VS Code

### PyCharm Plugin

For PyCharm users:

1. Install the FixLoop plugin from JetBrains Marketplace
2. Configure the plugin with your FixLoop server URL
3. Access FixLoop features through the PyCharm Tools menu

## Configuration

FixLoop can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Base URL for Ollama service | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default Ollama model to use | `llama3` |
| `OLLAMA_CODE_MODEL` | Specific model for code tasks | `codellama` |
| `CACHE_TTL` | Cache time-to-live in hours | `3` |
| `CACHE_MAX_SIZE` | Maximum cache size | `500` |

## Performance Tips

1. **Use the cache**: Repeated similar requests will be faster due to caching
2. **Batch related requests**: Use the batch API for multiple related code snippets
3. **Use appropriate models**: Different tasks benefit from different language models
4. **Consider code size**: Large code bases may need to be chunked for optimal performance

## Troubleshooting

### Common Issues

1. **Connection errors**: Ensure the FixLoop server is running and accessible
2. **Timeout errors**: Large code snippets may require increased timeout settings
3. **Memory issues**: Consider reducing model size or increasing system resources
4. **Incorrect results**: Try providing more context or simplifying the code

## Contributing

We welcome contributions to FixLoop! Please see our contributing guidelines for more information on how to get involved. 