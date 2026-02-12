# Project README Generation Agent

A Python-based AI agent that analyzes your codebase and generates a professional `README.md` file using Google's Gemini LLM.

## Table of Contents
- [Agent Design](#agent-design)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Assumptions](#assumptions)
- [Limitations](#limitations)

## Agent Design
The agent operates using a three-step process:
1.  **Recursive File Scanning**: The agent recursively scans the target directory, identifying supported files (e.g., `.py`, `.js`, `.md`) while adhering to strict exclusion patterns (e.g., `.git`, `__pycache__`). It uses `pathlib` for robust cross-platform path handling.
2.  **Context Aggregation**: It generates a visual directory tree and reads the content of each file. Rate-limiting safeguards are applied by truncating excessively large files to manage token usage.
3.  **LLM Generation**: The aggregated context (tree structure + file contents) is injected into a prompt for the Gemini LLM. The system prompt is engineered to instruct the model to act as a "Technical Writer," enforcing strict Markdown formatting and structure.

## Features
- **Project Structure Analysis**: Visualizes the directory tree to understand project organization.
- **Smart Truncation**: Automatically truncates files exceeding a configurable character limit (default: 5000) to prevent context window overflow.
- **Dry Run Mode**: Preview the file analysis and prompt construction without consuming API credits.
- **Robust Error Handling**: Gracefully handles encoding errors (falling back to Latin-1) and checks for API key validity.

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up API Key**:
    You need a valid Google Gemini API Key. Set it as an environment variable:
    - **Windows**: `set GEMINI_API_KEY=your_api_key_here`
    - **Mac/Linux**: `export GEMINI_API_KEY=your_api_key_here`

## Usage

### Basic Generation
To generate a README for a target directory:
```bash
python -m app path/to/your/project
```

### Dry Run (Preview)
To see what files are detected and preview the context without calling the LLM:
```bash
python -m app path/to/your/project --dry-run
```

### Configure Truncation
To change the maximum characters read per file (default 5000):
```bash
python -m app path/to/your/project --max-chars 2000
```

## Assumptions
- **UTF-8 Encoding**: The agent assumes source files are UTF-8 encoded but includes a fallback for Latin-1.
- **Gemini API Access**: The application requires network access to Google's Gemini API and a valid API key.
- **Standard Project Layout**: It assumes a standard file system layout.

## Limitations
- **Token Limits**: Extremely large projects with hundreds of files may still exceed the LLM's context window even with truncation. The current summary strategy is raw concatenation.
- **Context Depth**: The agent reads file content directly. It does not currently perform semantic summarization of files before sending them to the LLM, which balances detail with context size.