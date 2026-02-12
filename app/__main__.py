"""
Entry point for the Project README Generation Agent.
Handles CLI arguments and orchestrates the agent execution.
"""
import sys
import os
import argparse
from app.agents import READMEAgent

def main():
    """
    Main execution function.
    Parses command-line arguments and invokes the READMEAgent.
    """
    parser = argparse.ArgumentParser(description="Generate a README.md for your project using an LLM.")
    parser.add_argument("directory_path", help="Path to the directory to analyze.")
    parser.add_argument("--dry-run", action="store_true", help="Run without calling the LLM to see context and file summary.")
    parser.add_argument("--max-chars", type=int, default=5000, help="Maximum characters per file to read (default: 5000).")
    
    args = parser.parse_args()
    
    project_path = args.directory_path
    if not os.path.exists(project_path):
        print(f"Error: Directory '{project_path}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(project_path):
        print(f"Error: Path '{project_path}' is not a directory.")
        sys.exit(1)

    try:
        agent = READMEAgent(project_path, max_chars_per_file=args.max_chars)
        result = agent.generate(dry_run=args.dry_run)
        print(result)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
