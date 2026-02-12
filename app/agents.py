"""
Core agent logic for the Project README Generation Agent.
Contains the ReadmeAgent class which orchestrates file analysis and LLM interaction.
"""
import os
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from app.models import ProjectMap, FileSummary
from app.tools import list_files, read_file_content, generate_directory_tree

logger = logging.getLogger(__name__)

class READMEAgent:
    """
    Agent responsible for generating README.md files from codebase analysis.
    """
    
    def __init__(self, project_path: str, max_chars_per_file: int = 5000):
        """
        Initialize the READMEAgent.
        
        Args:
            project_path (str): Path to the project root directory.
            max_chars_per_file (int): Maximum characters to read per file (default: 5000).
        """
        self.project_path = project_path
        self.max_chars_per_file = max_chars_per_file
        # Configure Gemini API - expects API key in environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            logger.warning("GEMINI_API_KEY not found in environment variables. LLM calls will fail.")
            self.model = None

    def get_file_summaries(self) -> List[FileSummary]:
        """
        Scans the project and returns a list of FileSummary objects.
        
        Returns:
            List[FileSummary]: List of file summaries with content.
        """
        files = list_files(self.project_path)
        summaries = []
        
        for file_path in files:
            content = read_file_content(file_path)
            if content:
                # Calculate relative path for cleaner context
                try:
                    rel_path = file_path.relative_to(self.project_path)
                except ValueError:
                    rel_path = file_path.name
                
                # Truncate content if too long
                if len(content) > self.max_chars_per_file:
                    logger.info(f"Truncating {rel_path} (length {len(content)} > {self.max_chars_per_file})")
                    content = content[:self.max_chars_per_file] + "\n...(truncated)..."

                summaries.append(FileSummary(
                    path=str(rel_path),
                    extension=file_path.suffix,
                    content=content,
                    summary=f"Content of {rel_path}" # Placeholder description
                ))
        return summaries

    def construct_system_prompt(self) -> str:
        """
        Constructs the system prompt for the LLM.
        
        Returns:
            str: The system prompt.
        """
        return """
You are an expert Technical Writer and Developer Advocate. Your goal is to analyze a codebase and generate a professional, comprehensive, and clear README.md file.

Your output must be strictly in VALID MARKDOWN format.

You will be provided with:
1. A directory tree structure of the project.
2. The contents of key files in the project.

Your task is to:
1. **Analyze the Project Structure**: Understand the organization of the code.
2. **Analyze File Contents**: Determine the purpose of the modules, classes, and functions.
3. **Identify Key Information**:
    - Project Name and Description (What does it do?)
    - Key Features (What are the main capabilities?)
    - Installation Instructions (How to set it up? Look for requirements.txt, setup.py, etc.)
    - Usage Examples (How to run it? Look for __main__.py, cli commands, etc.)
    - Technologies Used (Languages, libraries, frameworks).
4. **Generate the README.md**:
    - Use a clear and professional structure.
    - Include Badges if applicable (e.g., Python version, License).
    - Write a compelling introduction.
    - Provide step-by-step installation and usage guides.
    - If you see tests, mention how to run them.

**Strict Output Rules:**
- The output must be ONLY the markdown content of the README.md.
- Do not include conversational filler like "Here is the README".
- Ensure all code blocks are properly fenced.
"""

    def generate(self, dry_run: bool = False) -> str:
        """
        Generates the README content.
        
        Args:
            dry_run (bool): If True, skips the LLM call and returns a preview.
            
        Returns:
            str: The generated README content or error message.
        """
        logger.info(f"Analyzing project at: {self.project_path}")
        
        # 1. Get Directory Tree
        tree = generate_directory_tree(self.project_path)
        
        # 2. Get File Contents
        summaries = self.get_file_summaries()
        logger.info(f"Found {len(summaries)} valid files to analyze.")
        
        if not summaries:
            return "Error: No valid files found in the directory. Cannot generate README."

        # 3. Construct Context
        context_str = f"# Project Directory Tree\n```\n{tree}\n```\n\n# File Contents\n"
        
        for summary in summaries:
            context_str += f"\n## File: {summary.path}\n```{summary.extension[1:] if summary.extension.startswith('.') else 'text'}\n{summary.content}\n```\n"

        if dry_run:
            logger.info("Dry run enabled. Skipping LLM call.")
            return f"""[DRY RUN MODE]
            
Analysis complete.
- Files found: {len(summaries)}
- Total context size (approx): {len(context_str)} characters

Preview of Context Sent to LLM:
{context_str[:1000]}...
"""

        # 4. Call LLM
        if not self.model:
             return f"ERROR: GEMINI_API_KEY not set. \n\nGenerated Context (Preview):\n{context_str[:500]}..."

        try:
            logger.info("Sending request to LLM...")
            system_prompt = self.construct_system_prompt()
            response = self.model.generate_content(
                contents=[system_prompt, f"Here is the codebase information:\n\n{context_str}"]
            )
            return response.text
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return f"Error generating README: {e}"
