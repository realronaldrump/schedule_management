import streamlit as st
from utils.database import get_schedule_data, get_all_rooms
import datetime

st.set_page_config(page_title="Detailed Schedule", page_icon="📅")

def main():
    st.title("📅 Detailed Schedule")

    # --- Filters in Sidebar ---
    with st.sidebar:
        st.header("Filters")
        # Calculate a default index: if current weekday (0=Mon,...,6=Sun) is between 0 and 4, use it;
        # otherwise default to 0 ("All")
        weekday = datetime.datetime.now().weekday()  # 0-6
        default_day_index = weekday + 1 if weekday < 5 else 0
        selected_day = st.selectbox(
            "Day",
            ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            index=default_day_index
        )
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