import sqlite3

DB_NAME="user.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_table():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            tg_id INTEGER PRIMARY KEY,
            full_name TEXT,
            phone TEXT,
            lat REAL,
            lon REAL
        )
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT UNIQUE
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_code TEXT,
            name TEXT UNIQUE,
            price INTEGER,
            description TEXT,
            image TEXT
            )
        """)


def add_user(tg_id, full_name, phone, lat, lon):
    with connect() as con:
        con.execute("""
        INSERT OR REPLACE INTO users(tg_id,full_name,phone,lat,lon)
        VALUES(?,?,?,?,?)
        """,(tg_id, full_name, phone, lat, lon))

def get_user(tg_id):
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT * FROM users WHERE tg_id=?
        """,(tg_id,))
        return cur.fetchone()

def get_product_by_category(code):
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT id, name FROM products WHERE category_code=?
        """,(code,))

        return cur.fetchall()

def get_product(product_id):
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT id, name, price, description, image FROM products WHERE id=?
        """,(product_id,))
        return cur.fetchone()

def get_category():
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT name,code FROM categories
        """)
        return cur.fetchall()

def update_name(tg_id,full_name):
    with connect() as con:
        con.execute(
        "UPDATE users SET full_name=? WHERE tg_id=?",
        (full_name,tg_id)
        )

def update_phone(tg_id,phone):
    with connect() as con:
        con.execute(
        "UPDATE users SET phone=? WHERE tg_id=?",
        (phone,tg_id)
        )


def add_category(name,code):
    with connect() as con:
        con.execute("""
        INSERT INTO categories(name,code)
        VALUES(?, ?)
        """,(name,code))

def add_product(name,price,description,image,category_code):
    with connect() as con:
        con.execute("""
        INSERT INTO products(name,price,description,image,category_code)
        VALUES(? , ?, ? , ? , ?)
        """,(name,price,description,image,category_code))

def list_categories():
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT name FROM categories
        """)
        return cur.fetchall()

def list_products(category_code):
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT name FROM products WHERE category_code=?
        """,(category_code,))
        return cur.fetchall()

def del_category(code):
    with connect() as con:
        con.execute("""
        DELETE FROM categories WHERE code=?
        """,(code,))

        con.execute(
            "DELETE FROM products WHERE category_code=?",
            (code,)
        )


def del_products(name):
    with connect() as con:
        con.execute("""
        DELETE FROM products WHERE name=?
        """,(name,))  

def get_name_product():
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT name FROM products
        """) 
        return [i[0] for i in cur.fetchall()]

def get_category_code(name):
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT code FROM categories WHERE name = ?
        """,(name,))

        result=cur.fetchone()

        if result:
            return result[0]

        return None

def change_product_name(name,old_name):
    with connect() as con:
        con.execute("""
        UPDATE products SET name = ? WHERE name = ?
        """,(name,old_name))

def change_product_price(price,old_name):
    with connect() as con:
        con.execute("""
        UPDATE products SET price = ? WHERE name = ?
        """,(price,old_name))
def change_product_desc(price,old_name):
    with connect() as con:
        con.execute("""
        UPDATE products SET desc = ? WHERE name = ?
        """,(price,old_name))

def change_product_image(price,old_name):
    with connect() as con:
        con.execute("""
        UPDATE products SET image = ? WHERE name = ?
        """,(price,old_name))

def get_all_users():
    with connect() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT tg_id from users
        """)
        return cur.fetchall()