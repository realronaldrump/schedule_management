import streamlit as st
from utils.database import get_schedule_data, get_all_instructors
import datetime

st.set_page_config(page_title="Instructor Schedules", page_icon="🧑🏫")

def main():
    st.title("🧑🏫 Instructor Schedules")

    # --- Select Instructor ---
    instructor = st.selectbox("Select Instructor", get_all_instructors())

    # --- Filter Data ---
    df = get_schedule_data(instructor=instructor)

    # --- Display Schedule ---
    if not df.empty:
        # --- Filters in Sidebar ---
        with st.sidebar:
            st.header("Filters")
            selected_day = st.selectbox("Day", ["All"] + ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], index=datetime.datetime.now().weekday() + 1)
            
        # --- Load and Filter Data ---
        df = get_schedule_data(
            meeting_day=None if selected_day == "All" else selected_day[:3],
            instructor=instructor
        )
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="card" style="margin-bottom: 10px; color: #8e44ad;">
                <b>{row['Course']}</b> - {row['Room']}<br>
                {row['Start Time'].strftime('%I:%M %p')} - {row['End Time'].strftime('%I:%M %p')}<br>
                <small>{row['Course Title']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No classes scheduled for this instructor.")

if __name__ == "__main__":
    main()