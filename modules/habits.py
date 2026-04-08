from utils.database import add_habit, log_habit, get_habits_for_today, delete_habit, get_all_habits, is_habit_scheduled, get_habit_data, get_done_dates, get_habit_total_count
import sqlite3
from datetime import date, timedelta, datetime
import time
import streamlit as st

def init_session():
    if "current_day" not in st.session_state:
        st.session_state.current_day = date.today()

def update_habit_status(h_id, target_date, user_id):
    current_state = st.session_state[f"habit_{h_id}_{target_date}"]
    new_status = 1 if current_state else 0
    log_habit(h_id, target_date, new_status, user_id) 

def calculate_streak(h_id, user_id):
    h_data = get_habit_data(h_id, user_id)
    if not h_data:
        return 0
    f_type, f_value, start_date_str = h_data
    start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    done_dates = get_done_dates(h_id, user_id)
    streak = 0
    check_date = date.today()

    while check_date >= start_dt:
        if is_habit_scheduled(check_date, f_type, f_value, start_dt):
            date_str = check_date.isoformat()
            if date_str in done_dates:
                streak += 1
            elif check_date == date.today():
                pass
            else:
                break

        check_date -= timedelta(days=1)
    return streak

def habits_window(user_id):
    init_session()
    tab1, tab2, tab3 = st.tabs(["Menage Habits", "Habits for today", "Analytics"])
    with tab1:
        st.subheader("Add a New Habit")
        new_habit_name = st.text_input("Habit Name", placeholder="e.g., Read 20 pages")
        
        start_date = st.date_input("Start Date", value=date.today())
        days_to_save = []
        freq_type = st.selectbox("Repeat", ["Daily", "Weekdays", "Weekends", "Specific Days", "Custom Interval"])

        if freq_type == "Weekdays":
            days_to_save = [0, 1, 2, 3, 4]
        elif freq_type == "Weekends":
            days_to_save = [5, 6]
        elif freq_type == "Specific Days":
            selected_days = st.multiselect("Select Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
            day_map = {"Mon" : 0, "Tue" : 1, "Wed" : 2, "Thu" : 3, "Fri" : 4, "Sat" : 5, "Sun" : 6}
            days_to_save = [day_map[d] for d in selected_days]
        elif freq_type == "Custom Interval":
            interval = st.number_input("Repeat every X days", min_value=1, value=2)
        elif freq_type == "Daily":
            days_to_save = [0, 1, 2, 3, 4, 5, 6]
        
        freq_value = ""
        if freq_type == "Custom Interval":
            freq_value = str(interval)
        else:
            freq_value = ",".join(map(str, days_to_save))

        if st.button("Create Habit"):
            if new_habit_name:
                try:
                    add_habit(new_habit_name, freq_type, freq_value, start_date, user_id)
                    st.success(f"Habit '{new_habit_name}' created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Maybe this habit already exists? Error: {e}")

        st.divider()
        st.subheader("Archive a Habit")

        active_habits = get_all_habits(user_id)

        if active_habits:
            habit_options = {name: h_id for h_id, name in active_habits}
            
            habit_to_delete = st.selectbox("Select a habit to archive", options=list(habit_options.keys()))
            
            if st.button("Archive selected"):
                h_id = habit_options[habit_to_delete]
                delete_habit(h_id, user_id)
                st.success(f"Habit '{habit_to_delete}' has been archived.")
                st.rerun()
        else:
            st.info("No active habits to archive.")

    with tab2:
        selected_day = st.date_input("Select Date", value = st.session_state.current_day)
        if selected_day != st.session_state.current_day:
            st.session_state.current_day = selected_day
            st.rerun()
        
        st.subheader(f"Plans for {selected_day.strftime('%A, %d %b')}")
        habits = get_habits_for_today(st.session_state.current_day, user_id)
        if not habits:
            st.info("Nothing planned for this day. Rest day?")
        else:
            for h_id, h_name, h_status in habits:
                st.checkbox(h_name, value=bool(h_status), key=f"habit_{h_id}_{selected_day}", on_change=update_habit_status, args=(h_id, selected_day, user_id))

    with tab3:
        st.header("Your Progress")
        active_habits = get_all_habits(user_id)

        if not active_habits:
            st.info("You don't have any active habits yet. Go to 'Manage Habits' and add some")
        
        else:
            any_progress_shown = False
            for h_id, h_name in active_habits:
                current_streak = calculate_streak(h_id, user_id)
                total_done = get_habit_total_count(h_id, user_id)
                
                if total_done > 0:
                    any_progress_shown = True
                    times_word = "time" if total_done == 1 else "times"
                    
                    st.subheader(f"✨ {h_name}")
                    col1, col2 = st.columns(2)
                    col1.metric("Current Streak", f"{current_streak} days")
                    col2.metric("Total Progress", f"{total_done} {times_word}")
                    
                    if total_done % 50 == 0:
                        st.write(f"🎉 **Amazing! You've reached {total_done} completions!**")
            
            if not any_progress_shown:
                st.info("Your habits are created, but you haven't marked any as 'done' yet. Check 'Habits for today' to start building your streaks!")