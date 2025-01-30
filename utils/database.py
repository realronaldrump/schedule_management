import sqlite3
import pandas as pd
from typing import List, Optional, Dict, Any

DATABASE_FILE = "data/schedule_data.db"

def create_database() -> None:
    """Creates the database table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT,
            course_title TEXT,
            meeting_day TEXT,
            start_time TEXT,  -- Store as TEXT for simplicity (or TIME if you prefer and adjust parsing)
            end_time TEXT,    -- Store as TEXT for simplicity (or TIME if you prefer and adjust parsing)
            instructor TEXT,
            room TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_data(df: pd.DataFrame) -> None:
    """Inserts data from a DataFrame into the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    df.to_sql('schedule', conn, if_exists='replace', index=False) # 'replace' will recreate the table if schema changed
    conn.close()

def get_schedule_data(
    meeting_day: Optional[str] = None,
    rooms: Optional[List[str]] = None,
    instructor: Optional[str] = None
) -> pd.DataFrame:
    """Retrieves schedule data from the database with optional filters."""
    conn = sqlite3.connect(DATABASE_FILE)
    query = "SELECT * FROM schedule WHERE 1=1"
    params: Dict[str, Any] = {}

    if meeting_day:
        query += " AND meeting_day = :meeting_day"
        params["meeting_day"] = meeting_day

    if rooms:
        placeholders = ', '.join(['?'] * len(rooms))
        query += f" AND room IN ({placeholders})"
        params = {**params, **{f"room{i}": room for i, room in enumerate(rooms)}}

    if instructor:
        query += " AND instructor = :instructor"
        params["instructor"] = instructor

    df = pd.read_sql_query(query, conn, params=params)

    # Convert 'start_time' and 'end_time' back to datetime.time objects after reading from DB
    df['Start Time'] = pd.to_datetime(df['start_time']).dt.time
    df['End Time'] = pd.to_datetime(df['end_time']).dt.time
    conn.close()
    return df

def get_all_instructors() -> List[str]:
    """Retrieves a list of all instructors."""
    conn = sqlite3.connect(DATABASE_FILE)
    instructors = pd.read_sql_query("SELECT DISTINCT instructor FROM schedule", conn)
    if not instructors.empty: # Check if DataFrame is empty before accessing columns
        instructors = instructors['instructor'].tolist()
    else:
        instructors = []
    conn.close()
    return instructors

def get_all_rooms() -> List[str]:
    """Retrieves a list of all rooms."""
    conn = sqlite3.connect(DATABASE_FILE)
    rooms_df = pd.read_sql_query("SELECT DISTINCT room FROM schedule", conn)
    if not rooms_df.empty: # Check if DataFrame is empty before accessing columns
        rooms = rooms_df['room'].tolist()
    else:
        rooms = []
    conn.close()
    return rooms

create_database()  # Initialize the database on startup