import streamlit as st
from utils.database import get_schedule_data, get_all_rooms
import pandas as pd
import datetime

st.set_page_config(page_title="Detailed Schedule", page_icon="📅")

def main():
    st.title("📅 Detailed Schedule")

    # --- Filters in Sidebar ---
    with st.sidebar:
        st.header("Filters")
        selected_day = st.selectbox("Day", ["All"] + ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], index=datetime.datetime.now().weekday() + 1)
        selected_rooms = st.multiselect("Rooms", get_all_rooms())
        
    # --- Load and Filter Data ---
    df = get_schedule_data(
        meeting_day=None if selected_day == "All" else selected_day[:3],
        rooms=selected_rooms
    )

    # --- Display Schedule ---
    st.dataframe(
        df[['Course', 'Course Title', 'Meeting Day', 'Room', 'Instructor', 'Start Time', 'End Time']]
        .sort_values(['Meeting Day', 'Start Time']),
        use_container_width=True
    )

if __name__ == "__main__":
    main()