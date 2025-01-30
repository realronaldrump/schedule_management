import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_schedule_data, get_all_rooms
import datetime

st.set_page_config(page_title="Room Utilization", page_icon="🏫")

def room_heatmap(df: pd.DataFrame) -> None:
    st.markdown("### Room Utilization Heatmap")
    
    heatmap_data = df.pivot_table(
        index='Room',
        columns='Meeting Day',
        values='Course',
        aggfunc='count',
        fill_value=0
    )
    
    days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    heatmap_data = heatmap_data.reindex(columns=days_order)
    
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Day", y="Room", color="Classes"),
        color_continuous_scale='Blues',
        aspect="auto"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("🏫 Room Utilization")

    # --- Filters in Sidebar ---
    with st.sidebar:
        st.header("Filters")
        selected_day = st.selectbox("Day", ["All"] + ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
        selected_rooms = st.multiselect("Rooms", get_all_rooms())

    # --- Load and Filter Data ---
    df = get_schedule_data(
        meeting_day=None if selected_day == "All" else selected_day,
        rooms=selected_rooms
    )

    # --- Room Utilization Metrics ---
    total_rooms = len(get_all_rooms())
    now = datetime.datetime.now().time()
    current_classes = df[
        (df['Start Time'] <= now) & (df['End Time'] >= now)
    ]
    rooms_in_use = current_classes['Room'].nunique()
    available_rooms = total_rooms - rooms_in_use

    st.metric(label="Total Rooms", value=total_rooms)
    st.metric(label="Rooms in Use", value=rooms_in_use)
    st.metric(label="Available Rooms", value=available_rooms)

    # --- Interactive Heatmap ---
    room_heatmap(df)

    # --- Room Details on Click (using st.session_state) ---
    if 'clicked_room' not in st.session_state:
        st.session_state.clicked_room = None

    # Display details for the clicked room
    if st.session_state.clicked_room:
        st.markdown(f"#### Schedule for Room: {st.session_state.clicked_room}")
        room_schedule = df[df['Room'] == st.session_state.clicked_room]
        st.dataframe(room_schedule)

if __name__ == "__main__":
    main()