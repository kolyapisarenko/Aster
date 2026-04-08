import streamlit as st
from modules import utilities, savings, habits
from utils.database import init_db

def main():
    st.set_page_config(page_title="Aster Core", page_icon="🤖")
    
    init_db()

    query_params = st.query_params
    if "user_id" in query_params:
        st.session_state.user_id = int(query_params["user_id"])
        st.query_params.clear()

    if "user_id" not in st.session_state:
        st.title("Access is restricted")
        st.info("Please open Aster Core via Telegram bot")
        st.stop()    
    
    user_id = st.session_state.user_id
    st.sidebar.title("Aster Core")

    menu = st.sidebar.radio("Menu", ["Home", "Utility Tracker", "Habit Tracker", "Savings Tracker", "Settings"])

    if menu == "Home":
        st.write("Welcome back! I'm Aster, your personal assistant.")
        
    elif menu == "Utility Tracker":
        utilities.utility_report_window(user_id)

    elif menu == "Savings Tracker":
        savings.savings_window(user_id)

    elif menu == "Habit Tracker":
        habits.habits_window(user_id)

if __name__ == "__main__":
    main()