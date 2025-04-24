#!/usr/bin/env python3
"""
Agentic RAG Team Application
Conduct research on a specific topic, evaluate, critically appraise, and compile a final report.
"""

import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv, find_dotenv  # type: ignore
import openai  # type: ignore

from src.pipeline import run_pipeline
from src.utils.cache import clear_cache, CACHE_DIR

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv(find_dotenv())

# Set OpenAI API key from .env file
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)
openai.api_key = api_key

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Agentic RAG Team Application")
    parser.add_argument("-d", "--output-dir", dest="output_dir", default="output",
                        help="Directory to save output files (default: output)")
    parser.add_argument("-s", "--steps-dir", dest="steps_dir", default="steps_taken",
                        help="Directory to save process logs (default: steps_taken)")
    parser.add_argument("topic", nargs='+', help="Topic to research")
    parser.add_argument("-o", "--output", dest="output_file",
                        help="Path to save final report (Markdown)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose mode: show full intermediate results and timings")
    parser.add_argument("--clear-cache", action="store_true",
                        help="Clear the search cache before running")
    args = parser.parse_args()

    # Clear cache if requested
    if args.clear_cache and CACHE_DIR.exists():
        count = clear_cache()
        print(f"Cache cleared: {count} files removed")

    # Join topic words into a single string
    topic = " ".join(args.topic)

    # Run the pipeline
    asyncio.run(run_pipeline(
        topic,
        args.output_file,
        args.verbose,
        args.output_dir,
        args.steps_dir
    ))

if __name__ == "__main__":
    main()