import sqlite3

def get_customer_by_phone(phone):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM customers WHERE phone = ?", (phone,))
    result = cur.fetchone()
    conn.close()
    
    if result:
        return {"id": result[0], "name": result[1], "phone": result[2]}
    return None

def get_total_debt(customer_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM transactions WHERE customer_id = ?", (customer_id,))
    total = cur.fetchone()[0]
    conn.close()
    return total if total else 0

def add_transaction(customer_id, amount, reason):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (customer_id, amount, reason) VALUES (?, ?, ?)", 
                (customer_id, amount, reason))
    conn.commit()
    conn.close()