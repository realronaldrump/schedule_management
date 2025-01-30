import streamlit as st
from utils.data_processing import load_and_process_data
from utils.database import insert_data
import os

st.set_page_config(page_title="Data Management", page_icon="📁")

def main():
    st.title("📁 Data Management")

    st.warning("This is an admin-only page. Changes made here will affect the entire application.")

    # --- Upload and Process Data ---
    with st.expander("Upload Schedule Data"):
        uploaded_file = st.file_uploader("Upload Schedule", type=["csv", "xlsx"])
        if uploaded_file:
            df = load_and_process_data(uploaded_file)
            if df is not None:
                st.success(f"Loaded {len(df)} entries")
                
                # Convert 'Start Time' and 'End Time' columns to time objects
                df['Start Time'] = df['Start Time'].apply(lambda x: x.strftime('%H:%M:%S'))
                df['End Time'] = df['End Time'].apply(lambda x: x.strftime('%H:%M:%S'))
                
                if st.button("Save to Database"):
                    insert_data(df)
                    st.success("Data saved to database!")

    # --- Other Data Management Tasks (Future) ---
    # Add options for:
    # - Viewing database content
    # - Editing entries (advanced)
    # - Deleting entries (advanced)
    # - Backing up/restoring the database

if __name__ == "__main__":
    main()