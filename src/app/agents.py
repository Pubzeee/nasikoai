import os
import logging
import time
from google import genai
from app.config import MODEL_NAME
# Connects to your file-scanning logic
from app.tools import generate_directory_tree, get_file_summaries 

logger = logging.getLogger(__name__)

class READMEAgent:
    def __init__(self, project_path: str, max_chars_per_file: int = 5000):
        # 1. Setup API Access
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your terminal.")
        
        self.client = genai.Client(api_key=api_key)
        self.project_path = project_path
        self.max_chars_per_file = max_chars_per_file

    def _get_context(self) -> str:
        """Uses tools.py to build a comprehensive view of your project."""
        logger.info(f"Gathering project context...")
        
        # Get the visual structure
        tree = generate_directory_tree(self.project_path)
        # Get the actual code snippets
        summaries = get_file_summaries(self.project_path, self.max_chars_per_file)
        
        context_parts = [
            "# Project Directory Tree",
            "```",
            tree,
            "```",
            "\n# File Contents"
        ]
        
        for summary in summaries:
            context_parts.append(f"## File: {summary.relative_path}")
            context_parts.append(f"```\n{summary.content}\n```")
            
        return "\n".join(context_parts)

    def generate(self, dry_run: bool = False) -> str:
        """The main method called by __main__.py to create the README."""
        context = self._get_context()
        
        if dry_run:
            return f"--- DRY RUN COMPLETE ---\nReview the gathered context above. No LLM was called."

        try:
            # 🛑 IMPORTANT: 12s delay to stay under Free Tier 5-Requests-Per-Minute limit
            print("Respecting API Quota: Waiting 12s cooldown...")
            time.sleep(12)
            
            prompt = (
                "Act as a professional software engineer. Based on the following "
                "project tree and file contents, generate a high-quality, "
                "comprehensive README.md in Markdown format. Include installation, "
                "usage, and a tech stack section.\n\n"
                f"{context}"
            )
            
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text

        except Exception as e:
            logger.error(f"LLM Generation failed: {str(e)}")
            return f"An error occurred while generating the README: {str(e)}"