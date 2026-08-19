import sys
from pathlib import Path

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.append(
        str(PROJECT_ROOT)
    )

import sqlite3
from utils.logger import logger


DB_PATH = "staff.db"


# ============================================================
# Database Connection
# ============================================================

def get_connection():
    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )


# ============================================================
# Create Tables
# ============================================================

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # Nurses
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nurses (
        nurse_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        date_of_joining TEXT NOT NULL,
        shift_start TEXT NOT NULL,
        shift_end TEXT NOT NULL,
        leave_balance INTEGER NOT NULL,
        availability TEXT NOT NULL
    )
    """)

    # --------------------------------------------------------
    # Lab Technicians
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_technicians (
        technician_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        assigned_room TEXT NOT NULL,
        date_of_joining TEXT NOT NULL,
        shift_start TEXT NOT NULL,
        shift_end TEXT NOT NULL,
        leave_balance INTEGER NOT NULL,
        availability TEXT NOT NULL
    )
    """)

    # --------------------------------------------------------
    # Doctors
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        specialization TEXT NOT NULL,
        years_of_experience INTEGER NOT NULL,
        availability_days TEXT NOT NULL,
        availability_start TEXT NOT NULL,
        availability_end TEXT NOT NULL,
        leave_status TEXT NOT NULL
    )
    """)

    conn.commit()

    cursor.close()
    conn.close()

    logger.info("Staff database tables created successfully.")


# ============================================================
# Insert Data
# ============================================================

def insert_data():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # Nurses - 10
    # --------------------------------------------------------

    nurses = [

        (1, "Ananya Rao", "Emergency",
         "2021-06-14", "07:00", "15:00", 8, "Available"),

        (2, "Priya Sharma", "Cardiology",
         "2020-03-10", "08:00", "16:00", 5, "Available"),

        (3, "Meera Nair", "Pediatrics",
         "2022-01-18", "15:00", "23:00", 10, "Available"),

        (4, "Kavya Reddy", "Emergency",
         "2019-09-22", "23:00", "07:00", 4, "Available"),

        (5, "Sneha Iyer", "General Medicine",
         "2021-11-05", "08:00", "16:00", 7, "On Leave"),

        (6, "Divya Menon", "Cardiology",
         "2023-02-13", "07:00", "15:00", 12, "Available"),

        (7, "Lakshmi Das", "Neurology",
         "2020-07-27", "15:00", "23:00", 6, "Available"),

        (8, "Pooja Verma", "Orthopedics",
         "2022-08-19", "08:00", "16:00", 9, "Available"),

        (9, "Ritu Kapoor", "ICU",
         "2018-12-03", "07:00", "15:00", 3, "Available"),

        (10, "Neha Joshi", "General Surgery",
          "2021-04-26", "15:00", "23:00", 8, "Available"),
    ]

    cursor.executemany("""
    INSERT OR REPLACE INTO nurses
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, nurses)


    # --------------------------------------------------------
    # Lab Technicians - 10
    # --------------------------------------------------------

    lab_technicians = [

        (1, "Arjun Patel", "Pathology", "P-03",
         "2020-05-11", "07:00", "15:00", 6, "Available"),

        (2, "Rahul Singh", "Pathology", "P-03",
         "2021-08-16", "15:00", "23:00", 8, "Available"),

        (3, "Vikram Rao", "Radiology", "I-12",
         "2019-02-21", "08:00", "16:00", 4, "Available"),

        (4, "Sanjay Kumar", "Radiology", "I-12",
         "2022-06-09", "15:00", "23:00", 10, "Available"),

        (5, "Kiran Shah", "Laboratory", "L-05",
         "2020-11-17", "07:00", "15:00", 7, "On Leave"),

        (6, "Manoj Verma", "Pathology", "P-04",
         "2023-01-12", "08:00", "16:00", 12, "Available"),

        (7, "Rakesh Mehta", "Microbiology", "M-02",
         "2018-09-04", "15:00", "23:00", 5, "Available"),

        (8, "Amit Joshi", "Radiology", "I-13",
         "2021-03-29", "07:00", "15:00", 9, "Available"),

        (9, "Nitin Das", "Biochemistry", "B-01",
         "2022-10-10", "08:00", "16:00", 6, "Available"),

        (10, "Deepak Nair", "Laboratory", "L-06",
          "2019-07-15", "23:00", "07:00", 3, "Available"),
    ]

    cursor.executemany("""
    INSERT OR REPLACE INTO lab_technicians
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, lab_technicians)


    # --------------------------------------------------------
    # Doctors - 10
    # --------------------------------------------------------

    doctors = [

        (1, "Dr. Arvind Rao", "Cardiology",
         "Interventional Cardiology", 14,
         "Monday-Friday", "09:00", "17:00", "Available"),

        (2, "Dr. Meera Sharma", "Neurology",
         "Clinical Neurology", 11,
         "Monday-Saturday", "10:00", "18:00", "Available"),

        (3, "Dr. Rajiv Menon", "General Medicine",
         "Internal Medicine", 16,
         "Monday-Friday", "08:00", "16:00", "Available"),

        (4, "Dr. Kavita Reddy", "Pediatrics",
         "Pediatric Medicine", 9,
         "Monday-Saturday", "09:00", "15:00", "Available"),

        (5, "Dr. Sanjay Kapoor", "Orthopedics",
         "Orthopedic Surgery", 13,
         "Tuesday-Saturday", "10:00", "18:00", "Available"),

        (6, "Dr. Priya Nair", "General Surgery",
         "General Surgery", 12,
         "Monday-Friday", "09:00", "17:00", "On Leave"),

        (7, "Dr. Amit Verma", "Radiology",
         "Diagnostic Radiology", 15,
         "Monday-Saturday", "08:00", "16:00", "Available"),

        (8, "Dr. Sneha Iyer", "Gastroenterology",
         "Gastroenterology", 10,
         "Monday-Friday", "11:00", "19:00", "Available"),

        (9, "Dr. Vikram Joshi", "Emergency",
         "Emergency Medicine", 8,
         "Monday-Sunday", "16:00", "00:00", "Available"),

        (10, "Dr. Neha Das", "Dermatology",
          "Clinical Dermatology", 7,
          "Monday-Friday", "09:00", "15:00", "Available"),
    ]

    cursor.executemany("""
    INSERT OR REPLACE INTO doctors
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, doctors)


    conn.commit()

    cursor.close()
    conn.close()

    logger.info("Staff data inserted successfully.")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    create_tables()
    insert_data()

    logger.info(
        "Staff database initialized successfully."
    )