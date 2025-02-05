import streamlit as st
from utils.database import get_schedule_data, get_all_rooms
import datetime
import pytz

st.set_page_config(page_title="Detailed Schedule", page_icon="📅")

def get_now_central():
    central = pytz.timezone("US/Central")
    return datetime.datetime.now(central)

def main():
    st.title("📅 Detailed Schedule")
    
    now = get_now_central()
    with st.sidebar:
        st.header("Filters")
        weekday = now.weekday()  # 0-6
        default_day_index = weekday + 1 if weekday < 5 else 0
        selected_day = st.selectbox(
            "Day",
            ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            index=default_day_index
        )
        selected_rooms = st.multiselect("Rooms", get_all_rooms())
        
    df = get_schedule_data(
        meeting_day=None if selected_day == "All" else selected_day[:3],
        rooms=selected_rooms
    )
    
    st.dataframe(
        df[['Course', 'Course Title', 'Meeting Day', 'Room', 'Instructor', 'Start Time', 'End Time']]
        .sort_values(['Meeting Day', 'Start Time']),
        use_container_width=True
    )

if __name__ == "__main__":
    main()