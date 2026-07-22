import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # customers
    cur.execute("""CREATE TABLE IF NOT EXISTS customers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP);""")
    
    # transactions
    cur.execute("""CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE);""")
    
    # products
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brand TEXT NOT NULL,
        category TEXT,
        description TEXT,
        price INTEGER NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        path_image TEXT)""")
    
    # users
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                user_id INTEGER UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP);""")

    # contact
    cur.execute("""CREATE TABLE IF NOT EXISTS contact(
                id INTEGER PRIMARY KEY CHECK (id = 1),
                message TEXT);""")

    cur.execute("""INSERT OR IGNORE INTO contact(id, message) VALUES (1,"راه ارتباطی")""")

    # Orders
    cur.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_address TEXT,
        customer_note TEXT,
        total_price INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Order Items
    cur.execute("""CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )""")

    conn.commit()
    conn.close()
if __name__ == "__main__":
    init_db()