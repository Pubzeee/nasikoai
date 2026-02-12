"""
Configuration settings for the Project README Generation Agent.
Defines supported file extensions and exclusion patterns.
"""
from typing import Set

SUPPORTED_EXTENSIONS: Set[str] = {'.py', '.js', '.ts', '.md', '.txt', '.html', '.css', '.json', '.yaml', '.yml', '.java', '.c', '.cpp', '.h', '.hpp'}
EXCLUSION_PATTERNS: Set[str] = {'.git', '__pycache__', 'node_modules', '.idea', '.vscode', 'venv', 'env', 'dist', 'build', 'coverage'}
