import sqlite3

def get_customer_by_phone(phone:str):
    """
    Find the customer by phone number and return the info.

    Args:
        phone(str):
            Phone number received from the seller for search it.

    Returns:
        dict: a dictionary containing numeric ID, name, and phone number
    """
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM customers WHERE phone = ?", (phone,))
    result = cur.fetchone()
    conn.close()
    
    if result:
        return {"id": result[0], "name": result[1], "phone": result[2]}
    return None

def get_total_debt(customer_id:int):
    """
    Calculate the amount from received id.

    Args:
        customer_id(int):
            Numerical id received from get_customer_by_phone function.
    Returns:
        int: total of amount (sum of all transactions).
    """
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM transactions WHERE customer_id = ?", (customer_id,))
    total = cur.fetchone()[0]
    conn.close()
    return total if total else 0

def add_transaction(customer_id:int, amount:int, reason:int):
    """
    Add transactions with received info.

    Args:
        customer_id(int):
            An numeric id for customer.
        amount(int):
            Received amount for add to the database.
        reason(int):
            A reason for apply tranactions.
    Returns:
        None
    """
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (customer_id, amount, reason) VALUES (?, ?, ?)", 
                (customer_id, amount, reason))
    conn.commit()
    conn.close()