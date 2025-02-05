import streamlit as st
from utils.database import create_database

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Campus Management", page_icon="🏫")

# --- Custom CSS ---
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Database Initialization ---
create_database()

# --- Simple Login (replace with a robust solution) ---
def get_manager_password():
    return "admin123"

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.title("Admin Login")
        password = st.sidebar.text_input("Password", type="password")
        if password:
            if password == get_manager_password():
                st.session_state.logged_in = True
                st.sidebar.success("Logged in!")
                st.rerun()  # re-run after login
            else:
                st.sidebar.error("Incorrect password")
        return  # Stop execution if not logged in

    st.sidebar.title("Navigation")
    # The sidebar navigation is handled automatically by Streamlit Pages

if __name__ == "__main__":
    main()