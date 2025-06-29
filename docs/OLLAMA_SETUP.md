# Setting Up Ollama for OpenFix Pro

This guide will walk you through setting up Ollama, which provides the AI models that power OpenFix Pro.

## What is Ollama?

Ollama is an open-source tool that allows you to run Large Language Models (LLMs) locally on your computer. This means you can use powerful AI capabilities without depending on cloud services or API keys.

## System Requirements

- **CPU**: Any x86-64 CPU (Intel or AMD)
- **RAM**: Minimum 8GB, recommended 16GB+
- **Disk Space**: At least 10GB free space
- **Operating System**: Windows 10/11, macOS 11+, or Linux (Ubuntu 20.04+)
- **GPU**: Optional but recommended for better performance

## Installation Steps

### Windows

1. Download the installer from [Ollama's official site](https://ollama.com/download)
2. Run the installer and follow the prompts
3. After installation, Ollama will start automatically as a system service

### macOS

1. Download the macOS application from [Ollama's official site](https://ollama.com/download)
2. Open the downloaded file and drag Ollama to your Applications folder
3. Launch Ollama from your Applications folder

### Linux

1. Run the following command:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. Start the Ollama service:
   ```bash
   ollama serve
   ```

## Downloading Required Models

OpenFix Pro uses two main models:

1. **llama3**: For general language understanding
2. **codellama**: Specifically optimized for code understanding and generation

To download these models, open a terminal or command prompt and run:

```bash
# Pull the general model
ollama pull llama3

# Pull the code-specialized model
ollama pull codellama
```

This may take some time depending on your internet connection, as the models are several gigabytes in size.

## Verifying Installation

To verify that Ollama is running correctly:

1. Open a terminal or command prompt
2. Run:
   ```bash
   ollama list
   ```
3. You should see both `llama3` and `codellama` in the list of available models

## Troubleshooting

### Ollama Not Starting

- **Windows**: Check if the Ollama service is running in Task Manager. If not, restart it from Services.
- **macOS**: Open Activity Monitor and check if Ollama is running. If not, relaunch it from Applications.
- **Linux**: Run `systemctl status ollama` to check the service status, or restart with `systemctl restart ollama`.

### Models Not Downloading

- Ensure you have a stable internet connection
- Check if you have enough disk space
- Try with `--verbose` flag: `ollama pull llama3 --verbose`

### Performance Issues

- If models are running slowly, consider using a GPU if available
- Adjust model parameters based on your hardware by creating a custom model configuration

## Using with Docker

If you're using the Docker setup provided with OpenFix Pro, Ollama will be automatically deployed as a container, and you don't need to install it separately on your host system. The docker-compose.yml file is already configured to pull and use the required Ollama image.

## Next Steps

Once Ollama is set up, return to the main README for instructions on running OpenFix Pro. 