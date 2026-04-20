import sqlite3

conn = sqlite3.connect("rifa.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        senha TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        numero INTEGER PRIMARY KEY,
        comprador TEXT,
        vendedor TEXT,
        pago INTEGER DEFAULT 0
    )
    """)

    conn.commit()
