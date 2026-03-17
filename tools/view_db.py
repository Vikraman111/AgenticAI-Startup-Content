import sqlite3
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "data/agent_registry.db"

def view_full_db():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        
        # We can use pandas to read the SQL directly into a beautiful table format
        # but we'll trim down the really long text fields (like raw_content) so it's readable
        query = """
        SELECT 
            status, 
            score, 
            title, 
            source_module, 
            url,
            created_at
        FROM artifacts 
        ORDER BY score DESC, created_at DESC
        """
        
        # Read into a pandas DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Configure pandas to print the table nicely in the terminal
        pd.set_option('display.max_rows', None)        # Show all rows
        pd.set_option('display.max_columns', None)     # Show all columns
        pd.set_option('display.width', 200)            # Wide format
        pd.set_option('display.max_colwidth', 50)      # Truncate long URLs/Titles
        
        print("\n" + "="*80)
        print(f"📊 FULL AGENT DATABASE VIEW ({len(df)} total articles)")
        print("="*80 + "\n")
        
        # Print a breakdown of how many articles are in each stage
        print("Status Counts:")
        print(df['status'].value_counts().to_string())
        print("\n" + "-"*80 + "\n")
        
        # Print the actual table data
        print(df)
        
    except sqlite3.OperationalError:
        print(f"❌ Could not find database at {DB_PATH}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    view_full_db()
