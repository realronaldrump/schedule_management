import streamlit as st
from utils.data_processing import load_and_process_data
from utils.database import insert_data
import os

st.set_page_config(page_title="Data Management", page_icon="📁")

def main():
    st.title("📁 Data Management")
    st.warning("This is an admin-only page. Changes made here will affect the entire application.")

    with st.expander("Upload Schedule Data"):
        uploaded_file = st.file_uploader("Upload Schedule", type=["csv", "xlsx"])
        if uploaded_file:
            df = load_and_process_data(uploaded_file)
            if df is not None:
                st.success(f"Loaded {len(df)} entries")
                
                # Convert time columns to strings
                df['start_time'] = df['start_time'].apply(lambda x: x.strftime('%H:%M:%S') if x else None)
                df['end_time'] = df['end_time'].apply(lambda x: x.strftime('%H:%M:%S') if x else None)
                
                if st.button("Save to Database"):
                    insert_data(df)
                    st.success("Data saved to database!")

if __name__ == "__main__":
    main()