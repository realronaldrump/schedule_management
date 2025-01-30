import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_schedule_data, get_all_rooms
import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Room Utilization", page_icon="🏫")
st_autorefresh(interval=10000, key="util_refresh")  # 10-second refresh

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

    # --- Current Room Status ---
    st.markdown("### Real-Time Room Status")
    
    # Get current utilization data
    today_day_name = datetime.datetime.now().strftime('%a')
    df_today = get_schedule_data(meeting_day=today_day_name)
    now = datetime.datetime.now().time()
    
    # Calculate room statuses
    all_rooms = get_all_rooms()
    current_classes = df_today[
        (df_today['Start Time'] <= now) & 
        (df_today['End Time'] >= now)
    ]
    occupied_rooms = current_classes['Room'].unique().tolist()
    available_rooms = list(set(all_rooms) - set(occupied_rooms))
    
    # Sort rooms naturally
    occupied_rooms.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    available_rooms.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))

    # Display room status columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card" style="background-color: #fee2e2;">'
                    f'<div class="metric-value">🚫 {len(occupied_rooms)}</div>'
                    f'<div class="metric-label">Occupied Rooms</div></div>', 
                    unsafe_allow_html=True)
        
        if occupied_rooms:
            with st.expander("View Occupied Rooms", expanded=True):
                for room in occupied_rooms:
                    classes = current_classes[current_classes['Room'] == room]
                    st.markdown(f"""
                    **{room}**  
                    {classes.iloc[0]['Start Time'].strftime('%I:%M %p')} - {classes.iloc[0]['End Time'].strftime('%I:%M %p')}  
                    *{classes.iloc[0]['Course']} - {classes.iloc[0]['Course Title']}*  
                    👩🏫 {classes.iloc[0]['Instructor']}
                    """)
                    if len(classes) > 1:
                        st.caption(f"+ {len(classes)-1} more concurrent classes")
        else:
            st.info("No rooms currently in use")

    with col2:
        st.markdown(f'<div class="metric-card" style="background-color: #dcfce7;">'
                    f'<div class="metric-value">✅ {len(available_rooms)}</div>'
                    f'<div class="metric-label">Available Rooms</div></div>', 
                    unsafe_allow_html=True)
        
        if available_rooms:
            with st.expander("View Available Rooms", expanded=True):
                cols = st.columns(3)
                for i, room in enumerate(available_rooms):
                    cols[i%3].markdown(f"🏫 {room}")
        else:
            st.warning("All rooms are currently occupied")

    # --- Historical Analysis Section ---
    st.markdown("---")
    st.markdown("### Historical Utilization Patterns")
    
    # Load filtered data
    df_filtered = get_schedule_data(
        meeting_day=None if selected_day == "All" else selected_day,
        rooms=selected_rooms
    )
    
    # Interactive Heatmap
    room_heatmap(df_filtered)

    # Detailed Schedule
    st.markdown("#### Detailed Schedule")
    if not df_filtered.empty:
        st.dataframe(
            df_filtered[['Meeting Day', 'Room', 'Course', 'Instructor', 'Start Time', 'End Time']]
            .sort_values(['Meeting Day', 'Start Time']),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No classes found for selected filters")

if __name__ == "__main__":
    main()