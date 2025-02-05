import pandas as pd
import datetime
from typing import Optional
import streamlit as st

DAYS_MAP = {
    'monday': 'Mon', 'tuesday': 'Tue', 'wednesday': 'Wed',
    'thursday': 'Thu', 'friday': 'Fri'
}

def parse_time(time_str: str) -> Optional[datetime.time]:
    """Parses a time string into a datetime.time object."""
    time_str = time_str.strip().upper()
    for fmt in ("%I:%M%p", "%I%p", "%H:%M", "%H%M"):
        try:
            return datetime.datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    return None

@st.cache_data(ttl=3600, show_spinner="Processing schedule data...")
def load_and_process_data(uploaded_file) -> Optional[pd.DataFrame]:
    """Loads and processes the uploaded schedule data."""
    if not uploaded_file:
        return None

    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Validate required columns
        required_columns = {'Course', 'Course Title', 'Meeting Pattern', 
                            'Meeting Time', 'Instructor', 'Room Number(s)'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            st.error(f"Missing required columns: {', '.join(missing)}")
            return None

        # Clean data: remove rows missing critical information and trim whitespace
        df = df.dropna(subset=['Meeting Pattern', 'Meeting Time', 'Room Number(s)'])
        df['Room Number(s)'] = df['Room Number(s)'].astype(str).str.strip()
        
        # Expand each row for multiple meeting days and multiple rooms
        expanded = []
        for _, row in df.iterrows():
            rooms = [r.strip() for r in str(row['Room Number(s)']).split(';')]
            days = [d.strip().lower() for d in str(row['Meeting Pattern']).split(',')]
            
            # Strip meeting time and split into start/end times
            meeting_time_str = str(row['Meeting Time']).strip()
            if '-' in meeting_time_str:
                start_time_str, end_time_str = meeting_time_str.split('-')
                start_time = parse_time(start_time_str)
                end_time = parse_time(end_time_str)
            else:
                start_time = parse_time(meeting_time_str)
                end_time = None

            # Only add row if both start_time and end_time are available
            if start_time and end_time:
                for day in days:
                    for room in rooms:
                        if day in DAYS_MAP:
                            new_row = row.to_dict()
                            new_row['meeting_day'] = DAYS_MAP[day]
                            new_row['room'] = room
                            new_row['start_time'] = start_time
                            new_row['end_time'] = end_time
                            expanded.append(new_row)
        
        df_expanded = pd.DataFrame(expanded)
        
        # Keep only the needed columns
        keep_columns = [
            'Course', 'Course Title', 'meeting_day',
            'start_time', 'end_time', 'Instructor', 'room'
        ]
        df_expanded = df_expanded[keep_columns].dropna(subset=['start_time', 'end_time'])

        return df_expanded

    except Exception as e:
        st.error(f"Data processing error: {str(e)}")
        return None