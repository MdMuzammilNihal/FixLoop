# OpenFix Pro

A Free, Research-Grade Self-Correcting AI Coding Assistant with Optimization, Hinting, and Execution Support

## Features

- **Code Analysis**: Identify bugs, inefficiencies, and style issues
- **Code Optimization**: Improve time/space complexity while maintaining readability
- **Code Hints**: Get suggestions for improvement without full solutions
- **Code Fixing**: Automatically repair bugs and issues
- **Code Execution**: Run Python code in a secure sandbox
- **Fully Local Operation**: Uses Ollama for LLM inference without requiring API keys

## Quick Start

### Prerequisites

1. Install [Ollama](https://ollama.com/download) on your system
2. Pull the required models:
   ```bash
   ollama pull llama3
   ollama pull codellama
   ```

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/openfix-pro.git
   cd openfix-pro
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python openfix_pro.py
   ```

4. Open your browser and navigate to [http://localhost:8000](http://localhost:8000)

## Architecture

```
+--------------------+
|    User Interface  |
|  (Web Code Editor) |
+--------------------+
          |
          v
+-------------------------+          +------------------------+
|  Code Analyzer Agent    | <------> |  Hint Generator Agent   |
| - Static Checks         |          |  (if user wants help)   |
| - Code Explanation      |          +------------------------+
| - Function Descriptions |
| - Optimization Engine   |
+-------------------------+
          |
          v
+-------------------------+
| Self-Correcting Engine  |
| - Coder Agent           |
| - Reviewer Agent        |
| - Error Localizer       |
| - Fixer Agent           |
| - Validator Agent       |
| - Test Generator        |
+-------------------------+
          |
          v
+-------------------------+
| Code Execution Sandbox  |
| - Compile               |
| - Run with Input        |
| - Show Output           |
+-------------------------+
          |
          v
+---------------------------+
| Code Application Decision |
| (Apply AI Fix or Manual)  |
+---------------------------+
```

## Tech Stack

- **Backend**: FastAPI, Uvicorn, Ollama (for LLM integration)
- **Frontend**: HTML, CSS, JavaScript, Monaco Editor
- **Models**: Llama3 (general), CodeLlama (code-specific)
- **Code Execution**: Python subprocess with security measures

## Configuration

You can configure the application through environment variables:

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_CODE_MODEL=codellama
```

## Security Notes

The code execution sandbox implements several security measures:
1. Static AST analysis to block potentially dangerous imports
2. Execution timeout (5 seconds)
3. Subprocess isolation

However, this is still a development tool and should not be deployed in production environments without additional security hardening.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Project Structure

```
backend/
  api/           # Main backend and evaluation scripts
  evaluation/    # Evaluation reports and outputs
  fixes/         # Code fix and patch scripts
  tests/         # All test files
  data/          # Data files (CSVs, txt, keys)
  results/       # Output images, plots, and result files
  utils/         # Utility scripts
  requirements.txt
frontend/
  public/        # Static frontend assets
vscode-extension/ # VSCode extension code
docker/          # Dockerfile, docker-compose.yml, env.example
docs/            # Documentation (README, usage guides, setup)
checkpoints/     # Model checkpoints
evaluation_results/ # (Legacy or extra evaluation outputs)
venv/            # Python virtual environment (should be gitignored)
```

## Quickstart
1. Clone the repo
2. Set up Python and Node.js environments
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Run backend and frontend (see docker/ for Docker Compose)

## Contribution Guidelines
- Use feature branches and submit PRs
- Write tests for new features
- Keep code modular and documented

## License
MIT 