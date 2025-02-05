import sqlite3
import pandas as pd
from typing import List, Optional

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
            start_time TEXT,
            end_time TEXT,
            instructor TEXT,
            room TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_data(df: pd.DataFrame) -> None:
    """Inserts data from a DataFrame into the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    
    # Rename columns to match the database schema
    df = df.rename(columns={
        'Course': 'course',
        'Course Title': 'course_title',
        'Instructor': 'instructor'
    })
    
    # Replace existing data with the new dataset.
    df.to_sql('schedule', conn, if_exists='replace', index=False)
    conn.close()

def get_schedule_data(
    meeting_day: Optional[str] = None,
    rooms: Optional[List[str]] = None,
    instructor: Optional[str] = None
) -> pd.DataFrame:
    """Retrieves schedule data from the database with optional filters."""
    conn = sqlite3.connect(DATABASE_FILE)
    query = "SELECT * FROM schedule WHERE 1=1"
    params = []

    if meeting_day:
        query += " AND meeting_day = ?"
        params.append(meeting_day)

    if rooms:
        placeholders = ', '.join(['?'] * len(rooms))
        query += f" AND room IN ({placeholders})"
        params.extend(rooms)

    if instructor:
        query += " AND instructor = ?"
        params.append(instructor)

    df = pd.read_sql_query(query, conn, params=params)

    # Convert time strings back into time objects.
    # Since the times in the DB are stored in '%H:%M:%S' format and are in US/Central,
    # we directly localize them to US/Central.
    df['Start Time'] = pd.to_datetime(df['start_time'], format='%H:%M:%S') \
                         .dt.tz_localize('US/Central').dt.time
    df['End Time'] = pd.to_datetime(df['end_time'], format='%H:%M:%S') \
                         .dt.tz_localize('US/Central').dt.time

    # Rename columns for display purposes.
    df = df.rename(columns={
        'course': 'Course',
        'course_title': 'Course Title',
        'instructor': 'Instructor',
        'room': 'Room',
        'meeting_day': 'Meeting Day'
    })

    conn.close()
    return df

def get_all_instructors() -> List[str]:
    """Retrieves a list of all instructors."""
    conn = sqlite3.connect(DATABASE_FILE)
    instructors = pd.read_sql_query("SELECT DISTINCT instructor FROM schedule", conn)
    conn.close()
    return instructors['instructor'].tolist() if not instructors.empty else []

def get_all_rooms() -> List[str]:
    """Retrieves a list of all rooms."""
    conn = sqlite3.connect(DATABASE_FILE)
    rooms_df = pd.read_sql_query("SELECT DISTINCT room FROM schedule", conn)
    conn.close()
    return rooms_df['room'].tolist() if not rooms_df.empty else []

create_database()