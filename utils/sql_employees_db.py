import sqlite3
from logger import logger

conn = sqlite3.connect("employees.db", check_same_thread=False)
cursor = conn.cursor()

#create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
id INTEGER PRIMARY KEY,
name TEXT,
dept TEXT,
salary INTEGER,
email TEXT,
phone INTEGER,
date of joining TEXT
)
""")

#insert values
cursor.executemany("""
INSERT OR REPLACE INTO employees VALUES(?, ?, ?, ?, ?, ?, ?)
""", [
    (1, "harry", "AI", 50000, "harry@gmail.com", 7386123456, "NOV-2025"),
    (2, "shiv", "HR", 80000, "shiv@gmail.com", 9386123456, "DEC-2025"),
    (3, "ram", "finance", 70000, "ram@gmail.com", 8386123456, "JAN-2025"),
])

conn.commit()
cursor.close()
conn.close()

logger.info("employees db is created successfully....")