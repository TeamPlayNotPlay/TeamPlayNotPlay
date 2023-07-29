import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect('base.db')
    c = conn.cursor()
    c.execute("UPDATE guilds SET verify_webhook = ?;", ("no"))
    conn.commit()
    conn.close()