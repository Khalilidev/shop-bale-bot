import sqlite3
def new_user(user_id:int, user_name:str):
    """
    Add new user to database
    Args:
        user_id(int):
            user id like (123456)
        user_name(str): 
            user name like @abcd
    """
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (user_name, user_id) VALUES (?, ?)", (user_name, user_id))
        conn.commit()
        print(f"Added new user : {user_id}")
    except sqlite3.IntegrityError:
        print(f"{user_id} exists!")
    conn.close()