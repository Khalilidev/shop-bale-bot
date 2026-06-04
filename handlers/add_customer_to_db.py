import sqlite3
def add_customer(name:str, phone:str, amount:int, reason:str):
    """
    Add new customer to database if not exists or update the amount.

    Args:
        name(str):
            name of customer.
        phone(str):
            phone number of customer.
        amount(int):
            new amount received from seller.
        reason(str):
            reason of the amount.

    Returns:
        None
    """
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT id FROM customers WHERE phone = ?",(phone,))
    result = cur.fetchone()

    # there is not customer
    if result == None:
        cur.execute("INSERT INTO customers (name, phone) VALUES (? , ?)", (name, phone))
        customer_id = cur.lastrowid
        conn.commit()
    
    # there is customer
    else : customer_id = result[0]

    cur.execute("INSERT INTO transactions(customer_id, amount, reason) VALUES(?, ?, ?)", (customer_id, amount, reason))
    conn.commit()
    conn.close()