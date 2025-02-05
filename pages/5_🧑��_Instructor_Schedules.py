import streamlit as st
from utils.database import get_schedule_data, get_all_instructors
import datetime
import pytz

st.set_page_config(page_title="Instructor Schedules", page_icon="🧑🏫")

def get_now_central():
    central = pytz.timezone("US/Central")
    return datetime.datetime.now(central)

def main():
    st.title("🧑🏫 Instructor Schedules")
    
    instructors = get_all_instructors()
    if not instructors:
        st.info("No instructors found in the database.")
        return
    instructor = st.selectbox("Select Instructor", instructors)
    
    df = get_schedule_data(instructor=instructor)
    
    if not df.empty:
        now = get_now_central()
        with st.sidebar:
            st.header("Filters")
            weekday = now.weekday()
            default_day_index = weekday + 1 if weekday < 5 else 0
            selected_day = st.selectbox(
                "Day",
                ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                index=default_day_index
            )
            
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