import sqlite3
import json
from uuid import UUID

def check_and_delete():
    conn = sqlite3.connect('vault.db')
    cursor = conn.cursor()
    
    # Check current count
    cursor.execute('SELECT count(*) FROM notes')
    count = cursor.fetchone()[0]
    print(f"Initial count: {count}")
    
    if count > 0:
        # Get first ID
        cursor.execute('SELECT id FROM notes LIMIT 1')
        row = cursor.fetchone()
        if row:
            note_id = row[0]
            print(f"Attempting to delete ID: {note_id}")
            
            # Try deletion
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            conn.commit()
            
            # Verify deletion
            cursor.execute('SELECT count(*) FROM notes')
            new_count = cursor.fetchone()[0]
            print(f"Count after deletion attempt: {new_count}")
            
            if count == new_count:
                print("FAILURE: The row was not deleted from the database.")
            else:
                print("SUCCESS: The row was deleted.")
        else:
            print("No notes found to delete.")
    else:
        print("Database is already empty.")
    
    conn.close()

if __name__ == "__main__":
    check_and_delete()
