import sqlite3

def get_connection():
    return sqlite3.connect("students.db")

def setup_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT,
        name TEXT,
        department TEXT,
        phone TEXT,
        email TEXT,
        obtained_marks REAL,
        total_marks REAL,
        attendance REAL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        semester INTEGER,
        subject_name TEXT,
        obtained_marks REAL,
        max_marks REAL,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_extra_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        field_name TEXT,
        field_value TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    """)
    
    # NEW FEATURE: Safe migration for profile pictures
    try: cursor.execute("ALTER TABLE students ADD COLUMN profile_pic TEXT")
    except sqlite3.OperationalError: pass
        
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin123')")
    
    conn.commit()
    conn.close()