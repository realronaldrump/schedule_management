import streamlit as st
import datetime
from streamlit_autorefresh import st_autorefresh
from utils.database import get_schedule_data, get_all_rooms
import plotly.express as px
import pandas as pd
import pytz

# --- Configuration and Auto-Refresh ---
st.set_page_config(page_title="Dashboard", page_icon="🏠")
st_autorefresh(interval=10000, key="dashboard_refresh")

def get_current_time_and_week():
    central = pytz.timezone('US/Central')
    now = datetime.datetime.now(datetime.timezone.utc).astimezone(central)
    return now.strftime("%I:%M %p"), now.strftime('%A, %b %d %Y'), now.isocalendar()[1]

def create_timeline_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No schedule data for selected day")
        return

    # Ensure the Room column is treated as a string (discrete category)
    df["Room"] = df["Room"].astype(str)
    # Create an ordered list of rooms (sorted numerically if possible)
    room_order = sorted(df["Room"].unique(), key=lambda x: int(x) if x.isdigit() else x)

    # Create datetime objects for today using the schedule times
    base_date = datetime.date.today()
    df = df.copy()
    df['Start'] = df['Start Time'].apply(lambda t: datetime.datetime.combine(base_date, t))
    df['End'] = df['End Time'].apply(lambda t: datetime.datetime.combine(base_date, t))

    # Build the timeline chart with a forced category order for the y-axis
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

    # Force the y-axis to be categorical (this prevents Plotly from creating numeric ticks)
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=room_order)

    # Get current datetime for today
    current_dt = datetime.datetime.combine(datetime.date.today(), datetime.datetime.now().time())

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
    # Use abbreviated weekday name (e.g., "Mon", "Tue", etc.)
    today_abbr = datetime.datetime.now().strftime('%a')
    df = get_schedule_data(meeting_day=today_abbr)
    total_rooms = len(get_all_rooms())
    now_time = datetime.datetime.now().time()
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