import os

# Model name for the generation
MODEL_NAME = "gemini-2.0-flash"

# Missing variable that caused your error
SUPPORTED_EXTENSIONS = [".py", ".md", ".txt", ".json", ".yml", ".yaml", ".html", ".css", ".js"]

# Folders and files to skip
EXCLUSION_PATTERNS = [
    "__pycache__",
    ".git",
    "venv",
    ".env",
    "node_modules",
    "*.pyc",
    "dist",
    "build"
]