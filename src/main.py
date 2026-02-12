"""
Entry point for the application.
"""
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.__main__ import main

if __name__ == "__main__":
    main()
