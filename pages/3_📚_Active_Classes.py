import streamlit as st
import datetime
from utils.database import get_schedule_data

st.set_page_config(page_title="Active Classes", page_icon="📚")

def main():
    st.title("📚 Active Classes")

    # --- Load Data ---
    df = get_schedule_data()

    # --- Filter for Active Classes ---
    now = datetime.datetime.now().time()
    active_classes = df[
        (df['Meeting Day'] == datetime.datetime.now().strftime('%a')) &
        (df['Start Time'] <= now) &
        (df['End Time'] >= now)
    ]

    # --- Display Active Classes ---
    if active_classes.empty:
        st.warning("No active classes at the moment.")
    else:
        st.dataframe(
            active_classes[['Course', 'Course Title', 'Room', 'Instructor', 'Start Time', 'End Time']]
            .sort_values('Start Time'),
            use_container_width=True
        )

if __name__ == "__main__":
    main()