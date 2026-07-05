from flask import Flask
import sqlite3

def get_db_connection():
    import os
    directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory, "todo.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)
                 """)
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 title TEXT NOT NULL,
                 description TEXT NOT NULL,
                 completed BOOLEAN DEFAULT 0,
                 FOREIGN KEY (user_id) REFERENCES users(id))
                 """)
    conn.commit()
    conn.close()
    return