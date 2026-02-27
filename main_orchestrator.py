import sqlite3

def purge_junk():
    conn = sqlite3.connect('data/agent_registry.db') # Check your DB name
    cursor = conn.cursor()
    
    # Delete anything containing lifestyle keywords
    junk_words = ['mattress', 'shaver', 'sunscreen', 'walmart', 'exfoliator']
    for word in junk_words:
        cursor.execute("DELETE FROM artifacts WHERE title LIKE ?", (f'%{word}%',))
    
    conn.commit()
    print(f"🧹 Purged {conn.total_changes} junk entries from database.")
    conn.close()

if __name__ == "__main__":
    purge_junk()