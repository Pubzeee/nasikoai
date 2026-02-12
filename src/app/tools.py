import os
from pathlib import Path
from dataclasses import dataclass
from app.config import EXCLUSION_PATTERNS, SUPPORTED_EXTENSIONS

@dataclass
class FileSummary:
    relative_path: str
    content: str

def generate_directory_tree(root_path: str, indent: str = "") -> str:
    """Generates a visual tree of the project structure."""
    root = Path(root_path)
    tree = []
    
    # Get sorted list of files/dirs, filtering out exclusions
    items = sorted([item for item in root.iterdir() if item.name not in EXCLUSION_PATTERNS])
    
    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        
        tree.append(f"{indent}{connector}{item.name}")
        
        if item.is_dir():
            extension = "    " if is_last else "│   "
            tree.append(generate_directory_tree(item, indent + extension))
            
    return "\n".join(tree)

def get_file_summaries(root_path: str, max_chars: int) -> list:
    """Recursively finds valid files and reads their content."""
    summaries = []
    root = Path(root_path)
    
    for file_path in root.rglob("*"):
        # Skip directories and excluded patterns
        if file_path.is_dir() or any(part in EXCLUSION_PATTERNS for part in file_path.parts):
            continue
            
        # Only read supported file types (from config.py)
        if file_path.suffix in SUPPORTED_EXTENSIONS:
            try:
                content = file_path.read_text(encoding="utf-8")
                # Truncate to save tokens/characters
                if len(content) > max_chars:
                    content = content[:max_chars] + "\n... [Content Truncated] ..."
                
                rel_path = file_path.relative_to(root)
                summaries.append(FileSummary(relative_path=str(rel_path), content=content))
            except Exception as e:
                # Silently skip files that can't be read (binary, encoding issues)
                continue
                
    return summaries