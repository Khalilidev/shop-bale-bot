import sqlite3
def get_text():
    """
    Get the contact text from the database and return it.
    Args:
        None
    Returns:    
        (str):
            Return the saved contact in database.
    """
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT message FROM contact WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row[0]