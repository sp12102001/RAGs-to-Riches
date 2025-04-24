#!/usr/bin/env python3
"""
Verify that all imports are working correctly
"""

def verify_imports():
    """Check all module imports"""
    print("Verifying imports...")

    # Check utils imports
    try:
        from src.utils.cache import load_from_cache, save_to_cache, clear_cache
        from src.utils.formatting import safe_str, sanitize_filename, get_timestamp
        print("✅ Utils imports successful")
    except ImportError as e:
        print(f"❌ Utils imports failed: {e}")

    # Check tools imports
    try:
        from src.tools import web_search, openalex_search, crossref_search
        print("✅ Tools imports successful")
    except ImportError as e:
        print(f"❌ Tools imports failed: {e}")

    # Check agents imports
    try:
        from src.agents import research_agent, evaluation_agent, appraisal_agent, report_agent
        print("✅ Agents imports successful")
    except ImportError as e:
        print(f"❌ Agents imports failed: {e}")

    # Check pipeline imports
    try:
        from src.pipeline import run_pipeline
        print("✅ Pipeline imports successful")
    except ImportError as e:
        print(f"❌ Pipeline imports failed: {e}")

    # Check main imports
    try:
        import main
        print("✅ Main imports successful")
    except ImportError as e:
        print(f"❌ Main imports failed: {e}")

    print("Verification complete")

if __name__ == "__main__":
    verify_imports()