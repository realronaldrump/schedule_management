import streamlit as st
import datetime
from streamlit_autorefresh import st_autorefresh
from utils.database import get_schedule_data, get_all_rooms
import plotly.express as px
import pandas as pd

# --- Configuration and Auto-Refresh ---
st.set_page_config(page_title="Dashboard", page_icon="🏠")
st_autorefresh(interval=10000, key="dashboard_refresh")

def get_current_time_and_week():
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p"), now.strftime('%A, %b %d %Y'), now.isocalendar()[1]

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
        title="Live Schedule Timeline",
        labels={'Room': 'Room Number'},
        hover_data=['Course Title', 'Instructor'],
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Add current time line
    now = datetime.datetime.now()
    fig.add_vline(
        x=now.timestamp() * 1000,
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
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="sans-serif"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    current_time, current_date, week_number = get_current_time_and_week()

    # --- Header ---
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f'<div class="time-display">{current_time}</div>', unsafe_allow_html=True)
        st.caption(f"📅 {current_date} | Week {week_number}")
    with col2:
        st.title("Campus Dashboard")
        st.markdown("---")

    # --- Status Cards ---
    df = get_schedule_data(meeting_day=datetime.datetime.now().strftime('%a'))
    total_rooms = len(get_all_rooms())
    now = datetime.datetime.now().time()
    current_classes = df[(df['Start Time'] <= now) & (df['End Time'] >= now)]
    rooms_in_use = current_classes['Room'].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">🏫 {}</div>
            <div class="metric-label">Total Rooms</div>
        </div>
        """.format(total_rooms), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">📚 {}</div>
            <div class="metric-label">Rooms in Use</div>
        </div>
        """.format(rooms_in_use), unsafe_allow_html=True)
    
    with col3:
        upcoming = df[df['Start Time'] > now].shape[0]
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">⏭️ {}</div>
            <div class="metric-label">Upcoming Classes</div>
        </div>
        """.format(upcoming), unsafe_allow_html=True)

    # --- Timeline Chart ---
    st.markdown("### Live Schedule Overview")
    create_timeline_chart(df)

if __name__ == "__main__":
    main()