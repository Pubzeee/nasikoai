"""
Pydantic models for the Project README Generation Agent.
Defines the structure for file summaries and project maps.
"""
from pydantic import BaseModel
from typing import List, Optional

class FileSummary(BaseModel):
    """
    Represents a summary of a single file.
    
    Attributes:
        path (str): The relative path to the file.
        extension (str): The file extension.
        summary (Optional[str]): A brief summary or description of the file content.
        content (Optional[str]): The actual content of the file (potentially truncated).
    """
    path: str
    extension: str
    summary: Optional[str] = None
    content: Optional[str] = None

class ProjectMap(BaseModel):
    """
    Represents the map of the entire project.
    
    Attributes:
        files (List[FileSummary]): A list of file summaries.
        project_root (str): The absolute path to the project root.
    """
    files: List[FileSummary]
    project_root: str
