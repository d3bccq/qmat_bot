#Это файл для работы с бд
import sqlite3 as sq
import datetime

db = sq.connect('db/database.db', check_same_thread=False)
cur = db.cursor()

#Создание таблицы статистики
cur.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER UNIQUE PRIMARY KEY NOT NULL, username TEXT, date TEXT, first_name TEXT, answer TEXT)")
db.commit()

#Добавление в таблицу статистики
def db_table_val(user_id: int, username: str, date:str, first_name:str, answer:str):
        cur.execute('REPLACE INTO users (user_id, username, date, first_name, answer) VALUES (?, ?, ?, ?, ?)', (user_id, username, date, first_name, answer))
        db.commit()

