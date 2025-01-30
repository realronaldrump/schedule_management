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

        # Validate
        required_columns = {'Course', 'Course Title', 'Meeting Pattern', 
                          'Meeting Time', 'Instructor', 'Room Number(s)'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            st.error(f"Missing required columns: {', '.join(missing)}")
            return None

        # Clean
        df = df.dropna(subset=['Meeting Pattern', 'Meeting Time', 'Room Number(s)'])
        df['Room Number(s)'] = df['Room Number(s)'].astype(str).str.strip()
        
        # Expand
        expanded = []
        for _, row in df.iterrows():
            rooms = [r.strip() for r in str(row['Room Number(s)']).split(';')]
            days = [d.strip().lower() for d in row['Meeting Pattern'].split(',')]
            
            # Correctly parse the time range
            if isinstance(row['Meeting Time'], str):
                start_time_str, end_time_str = row['Meeting Time'].split('-')
                start_time = parse_time(start_time_str)
                end_time = parse_time(end_time_str)
            else:
                start_time = None
                end_time = None

            for day in days:
                for room in rooms:
                    if day in DAYS_MAP:
                        new_row = row.copy()
                        new_row['Meeting Day'] = DAYS_MAP[day]
                        new_row['Room'] = room
                        new_row['Start Time'] = start_time
                        new_row['End Time'] = end_time
                        expanded.append(new_row)
        
        df_expanded = pd.DataFrame(expanded)
        
        df_expanded = df_expanded.dropna(subset=['Start Time', 'End Time'])

        return df_expanded

    except Exception as e:
        st.error(f"Data processing error: {str(e)}")
        return None