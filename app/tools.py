"""
Helper tools for file system operations.
Includes functions to list files, read content safely, and generate directory trees.
"""
import logging
import os
from pathlib import Path
from typing import List, Optional, Set
from app.config import SUPPORTED_EXTENSIONS, EXCLUSION_PATTERNS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def should_exclude(path: Path) -> bool:
    """
    Check if the path should be excluded based on config patterns.
    
    Args:
        path (Path): The file or directory path to check.
        
    Returns:
        bool: True if the path should be excluded, False otherwise.
    """
    for part in path.parts:
        if part in EXCLUSION_PATTERNS:
            return True
        # Handle glob-like patterns if needed, but simple string matching for now as per config
        if any(part.startswith(p) and len(p) > 1 for p in EXCLUSION_PATTERNS if p.startswith('.')):
             # This handles .git etc. logic if they are in the path parts
             pass 
    return False

def list_files(directory: str) -> List[Path]:
    """
    Recursively lists files while ignoring items in config.py.
    
    Args:
        directory (str): The root directory to search.
        
    Returns:
        List[Path]: A list of Path objects for supported files.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.error(f"Directory not found: {directory}")
        return []
    
    if not dir_path.is_dir():
        logger.error(f"Path is not a directory: {directory}")
        return []

    files_list = []
    
    try:
        # Walk through the directory
        for root, dirs, files in os.walk(dir_path):
            # Modify dirs in-place to exclude directories
            dirs[:] = [d for d in dirs if d not in EXCLUSION_PATTERNS]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check exclusion for file specifically (extensions etc)
                # Although config has EXCLUSION_PATTERNS like .git, which usually applies to dirs.
                # SUPPORTED_EXTENSIONS check
                if file_path.suffix not in SUPPORTED_EXTENSIONS:
                    continue
                    
                files_list.append(file_path)

        if not files_list:
            logger.warning(f"No matching files found in {directory}")

    except Exception as e:
        logger.error(f"Error listing files in {directory}: {e}")
        
    return files_list

def read_file_content(path: Path) -> Optional[str]:
    """
    Safely reads text, handling encoding errors.
    
    Args:
        path (Path): The path to the file to read.
        
    Returns:
        Optional[str]: The file content if read successfully, None otherwise.
    """
    try:
        # Try reading as UTF-8 first
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1 or similar if utf-8 fails, or just ignore errors?
            # User asked to handle encoding errors.
            logger.warning(f"Unicode decode error for {path}, trying latin-1")
            return path.read_text(encoding='latin-1')
        except Exception as e:
            logger.error(f"Failed to read file {path} with latin-1: {e}")
            return None
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return None

def generate_directory_tree(directory: str) -> str:
    """
    Creates a visual text representation of the folder structure.
    
    Args:
        directory (str): The root directory to visualize.
        
    Returns:
        str: A string representation of the directory tree.
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        return f"Invalid directory: {directory}"

    tree_str = f"{dir_path.name}/\n"
    
    def _add_to_tree(path: Path, prefix: str = ""):
        nonlocal tree_str
        
        # Get children, sorted, filtering exclusions
        try:
            entries = sorted([
                e for e in path.iterdir() 
                if e.name not in EXCLUSION_PATTERNS and not should_exclude(e)
            ], key=lambda e: (e.is_file(), e.name.lower()))
        except PermissionError:
            logger.error(f"Permission denied accessing {path}")
            return

        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            
            tree_str += f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}\n"
            
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _add_to_tree(entry, prefix + extension)

    _add_to_tree(dir_path)
    return tree_str
