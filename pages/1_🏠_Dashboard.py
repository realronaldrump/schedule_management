import streamlit as st
import datetime
import pytz
import pandas as pd
import plotly.express as px
from utils.database import get_schedule_data, get_all_rooms
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Dashboard", page_icon="🏠")
st_autorefresh(interval=10000, key="dashboard_refresh")

# Helper to get current US/Central time
def get_now_central():
    central = pytz.timezone("US/Central")
    return datetime.datetime.now(central)

def get_current_time_and_week():
    now = get_now_central()
    return now.strftime("%I:%M %p"), now.strftime('%A, %b %d %Y'), now.isocalendar()[1]

def create_timeline_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No schedule data for selected day")
        return

    # Ensure the Room column is treated as a string (discrete category)
    df["Room"] = df["Room"].astype(str)
    # Create an ordered list of rooms (sorted numerically if possible)
    room_order = sorted(df["Room"].unique(), key=lambda x: int(x) if x.isdigit() else x)

    # Use US/Central time for today
    now = get_now_central()
    base_date = now.date()

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
        color_discrete_sequence=px.colors.qualitative.Pastel,
        category_orders={"Room": room_order}
    )

    # Force the y-axis to be categorical using the room_order list
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=room_order)

    # Use our US/Central now for the vertical current-time marker
    current_dt = now  # already in US/Central

    # Add a vertical line at the current time using add_shape
    fig.add_shape(
        type="line",
        x0=current_dt,
        x1=current_dt,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(
            color="red",
            width=2,
            dash="dash"
        )
    )

    # Add an annotation to label the current time line
    fig.add_annotation(
        x=current_dt,
        y=1,
        xref="x",
        yref="paper",
        text="Current Time",
        showarrow=False,
        yanchor="bottom",
        font=dict(color="red")
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
            font_family="sans-serif",
            font_color="black"
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

    # Use US/Central time for calculations
    now = get_now_central()
    today_abbr = now.strftime('%a')
    
    # --- Status Cards ---
    df = get_schedule_data(meeting_day=today_abbr)
    total_rooms = len(get_all_rooms())
    now_time = now.time()
    current_classes = df[(df['Start Time'] <= now_time) & (df['End Time'] >= now_time)]
    rooms_in_use = current_classes['Room'].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">🏫 {total_rooms}</div>
            <div class="metric-label">Total Rooms</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">📚 {rooms_in_use}</div>
            <div class="metric-label">Rooms in Use</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        upcoming = df[df['Start Time'] > now_time].shape[0]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">⏭️ {upcoming}</div>
            <div class="metric-label">Upcoming Classes</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Timeline Chart ---
    st.markdown("### Live Schedule Overview")
    create_timeline_chart(df)

if __name__ == "__main__":
    main()
