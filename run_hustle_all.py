#!/usr/bin/env python3
"""
HUSTLE MASTER EXTRACTOR: Combines Gmail API + EML Archive
Runs both extractions and registers all articles into database.
"""

import sys
import subprocess

def run_extraction():
    """Run both Hustle extractions."""
    print("\n" + "="*80)
    print("📧 HUSTLE MASTER EXTRACTOR")
    print("="*80 + "\n")
    
    # ⭐ COMMENT OUT THE LINE BELOW AFTER FIRST RUN TO SKIP EML PROCESSING
    print("1️⃣  Importing EML archive (50 emails)...")
    result1 = subprocess.run([sys.executable, 'run_import_hustle_eml.py'], cwd='.')
    if result1.returncode != 0:
        print("⚠️  EML import had issues, continuing...")
    
    # Always run Gmail API extraction (fetches latest emails)
    print("\n2️⃣  Fetching latest emails via Gmail API...")
    result2 = subprocess.run([sys.executable, 'run_hustle_extraction.py'], cwd='.')
    if result2.returncode != 0:
        print("⚠️  Gmail extraction failed!")
        return False
    
    print("\n" + "="*80)
    print("✅ HUSTLE EXTRACTION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("   1. python3 run_understanding.py")
    print("   2. python3 run_scoring.py")
    print("   3. python3 run_insights.py")
    print("   4. python3 run_writer.py\n")
    
    return True

if __name__ == "__main__":
    success = run_extraction()
    sys.exit(0 if success else 1)
