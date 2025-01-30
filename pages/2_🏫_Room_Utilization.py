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
    
    fig.update_layout(
        height=500,
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="sans-serif"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("🏫 Room Utilization Analysis")
    st.markdown("---")

    # --- Filters in Sidebar ---
    with st.sidebar:
        st.header("🔍 Filters")
        selected_day = st.selectbox("Select Day", ["All"] + ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
        selected_rooms = st.multiselect("Select Rooms", get_all_rooms())

    # --- Load Data ---
    today_day_name = datetime.datetime.now().strftime('%a')
    df_today = get_schedule_data(meeting_day=today_day_name)  # For current utilization
    df_filtered = get_schedule_data(  # For historical analysis
        meeting_day=None if selected_day == "All" else selected_day,
        rooms=selected_rooms
    )

    # --- Current Utilization Metrics ---
    now = datetime.datetime.now().time()
    current_classes = df_today[
        (df_today['Start Time'] <= now) & 
        (df_today['End Time'] >= now)
    ]
    rooms_in_use = current_classes['Room'].nunique()
    total_rooms = len(get_all_rooms())
    available_rooms = total_rooms - rooms_in_use

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">🏫 {total_rooms}</div>
            <div class="metric-label">Total Rooms</div>
        </div>''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">📚 {rooms_in_use}</div>
            <div class="metric-label">Currently In Use</div>
        </div>''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">✅ {available_rooms}</div>
            <div class="metric-label">Available Now</div>
        </div>''', unsafe_allow_html=True)

    # --- Historical Analysis Section ---
    st.markdown("---")
    st.markdown("### Historical Utilization Patterns")
    
    # --- Interactive Heatmap ---
    room_heatmap(df_filtered)

    # --- Room Details Table ---
    st.markdown("### Detailed Room Schedule")
    if not df_filtered.empty:
        df_display = df_filtered[['Meeting Day', 'Room', 'Course', 'Instructor', 'Start Time', 'End Time']]
        st.dataframe(
            df_display.sort_values(['Meeting Day', 'Start Time']),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No classes found for selected filters")

if __name__ == "__main__":
    main()