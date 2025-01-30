import streamlit as st
import datetime
from streamlit_autorefresh import st_autorefresh
from utils.database import get_schedule_data, get_all_rooms
import plotly.express as px
import pandas as pd

# --- Configuration and Auto-Refresh ---
st.set_page_config(page_title="Dashboard", page_icon="🏠")
st_autorefresh(interval=10000, key="dashboard_refresh")  # 10 seconds

# --- Helper Functions ---
def get_current_time_and_week():
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p"), now.strftime('%A, %b %d %Y'), now.isocalendar()[1]

def get_next_class(df):
    now = datetime.datetime.now().time()
    today = datetime.datetime.now().strftime('%a')
    
    # Filter for today and future classes
    df_today = df[df['Meeting Day'] == today]
    df_future = df_today[df_today['Start Time'] > now]
    
    # Sort by start time to find the next class
    df_future_sorted = df_future.sort_values(by='Start Time')

    if not df_future_sorted.empty:
        next_class = df_future_sorted.iloc[0]  # Get the first row (next class)
        return f"{next_class['Course']} - {next_class['Room']}<br>{next_class['Start Time'].strftime('%I:%M %p')}"
    else:
        return "No upcoming classes"

def create_timeline_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No schedule data for selected day")
        return

    # Create datetime objects with today's date
    base_date = datetime.date.today()
    df = df.copy()
    df['Start'] = df['Start Time'].apply(lambda t: datetime.datetime.combine(base_date, t))
    df['End'] = df['End Time'].apply(lambda t: datetime.datetime.combine(base_date, t))

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Room",
        color="Course",
        title="Daily Schedule Timeline",
        labels={'Room': 'Room Number'},
        hover_data=['Course Title', 'Instructor'],
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Add current time line
    now = datetime.datetime.now()
    fig.add_vline(
        x=now.timestamp() * 1000,  # Convert to milliseconds
        line_width=2,
        line_dash="dash",
        line_color="red",
        annotation_text="Current Time"
    )

    fig.update_layout(
        height=600,
        xaxis_title="Time",
        yaxis_title="Rooms",
        xaxis=dict(
            type='date',
            tickformat="%I:%M %p"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Main Dashboard Logic ---
def main():
    current_time, current_date, week_number = get_current_time_and_week()

    # --- Load Data ---
    today_day_name = datetime.datetime.now().strftime('%a')
    df = get_schedule_data(meeting_day=today_day_name)

    # --- Header ---
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f'<div class="time-display">{current_time}</div>', unsafe_allow_html=True)
        st.caption(f"{current_date} | Week {week_number}")
    with col2:
        st.title("Campus Dashboard")

    # --- Status Cards ---
    total_rooms = len(get_all_rooms())
    now = datetime.datetime.now().time()
    current_classes = df[
        (df['Start Time'] <= now) & (df['End Time'] >= now)
    ]
    rooms_in_use = current_classes['Room'].nunique()
    available_rooms = total_rooms - rooms_in_use
    next_class_info = get_next_class(df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Rooms", value=total_rooms)
    with col2:
        st.metric(label="Rooms in Use", value=rooms_in_use)
    with col3:
        st.markdown(f"""
        <div class="card" style="color: #2ecc71;">
            <h3>⏭️ Next Upcoming</h3>
            <div style="margin: 15px 0">{next_class_info}</div>
            <div class="status-indicator upcoming">Starting Soon</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Timeline Chart ---
    st.markdown("---")
    create_timeline_chart(df)

if __name__ == "__main__":
    main()