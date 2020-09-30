import os
import sqlite3 as sql



def conn():
    db = sql.connect("csvs.db")
    return db

def insert_one_data(data):
    db = conn()
    cur = db.cursor()
    cur.execute("INSERT OR IGNORE INTO csv(path,name) VALUES(?,?)",data)
    db.commit()
    db.close()

def insert_multi_data(data):
    db = conn()
    cur = db.cursor()
    cur.executemany("INSERT OR IGNORE INTO csv(path,name) VALUES(?,?)",data)
    db.commit()
    db.close()


def get_all_names():
    db = conn()
    cur = db.cursor()
    cur.execute("SELECT name FROM csv")
    return cur.fetchall()

def read_one(id):
    db = conn()
    cur = cursor()
    cur.execute("SELECT * FROM csv WHERE id={}".format(id))
    data = cur.fetchone()
    return data


if __name__ == "__main__":
    path = "./files"
    files = [i[0] for i in get_all_names()]
    file_to_save = []
    for root,dirs,fn in os.walk("./files"):
        pass
    for f in fn:
        if f in files:
            continue
        f_path = os.path.join(path,f)
        file_to_save.append((os.path.abspath(f_path),f))

    if file_to_save:
        print(len(file_to_save))
        insert_multi_data(file_to_save)
    else:
        print("None")

