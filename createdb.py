import sqlite3 as sql



def create():
    db = sql.connect("csvs.db")
    cur = db.cursor()
    cur.execute("CREATE TABLE csv( \
    id INTEGER PRIMARY KEY AUTOINCREMENT, \
    path TEXT NOT NULL, \
    name TEXT NOT NULL);")
    db.close()

if __name__ == "__main__":
    create()
