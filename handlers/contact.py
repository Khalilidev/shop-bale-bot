import sqlite3

def edit_contact(text:str):
    """
    Edit the contact for show to the customers.
    Args:
        text(str): new text from the seller.
    Returns:
        None
    """
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("UPDATE contact SET message = ? WHERE id = 1", (text,))
    conn.commit()
    conn.close()
