from utils.database import feed_piggy_bank, get_current_balance, get_savings_history, get_calendar_events, update_savings_entry
import sqlite3
from datetime import date, datetime
import pandas as pd
import time
import streamlit as st
from streamlit_calendar import calendar

UKRAINIAN_TAX_COEFICIENT = 0.805

def get_daily_suggestion():
    day_of_week = date.today().weekday()
    return 25 if day_of_week >= 5 else 10

def calculate_daily_bonus(current_balance, p=0.03):
    daily_rate = p / 365
    projected_bonus = current_balance * daily_rate
    return projected_bonus * UKRAINIAN_TAX_COEFICIENT

def calculate_monthly_bonus(current_balance, p=0.03):
    return (calculate_daily_bonus(current_balance, p)) * 30

def calculate_real_monthly_history(history_df, p=0.03):
    daily_rate = (p / 365) * UKRAINIAN_TAX_COEFICIENT
    history_df["daily_profit"] = history_df["balance"] * daily_rate
    month = datetime.now().month
    history_df.index = pd.to_datetime(history_df.index)
    history_df = history_df[history_df.index.month == month]
    if history_df.empty:
        return 0.0
    actual_earned = history_df["daily_profit"].sum()
    return actual_earned

def check_today_deposit(user_id):
    from datetime import date
    history = get_savings_history(user_id)
    if history.empty:
        return False
    today = date.today().isoformat()
    return today in history.index.values

def init_session(user_id):
    if "balance" not in st.session_state:
        st.session_state.balance = get_current_balance(user_id)
    if "is_deposited" not in st.session_state:
        st.session_state.is_deposited = check_today_deposit(user_id)
    if "history" not in st.session_state:
        st.session_state.history = get_savings_history(user_id)
    if "calendar_events" not in st.session_state:
        st.session_state.calendar_events = get_calendar_events(user_id)
    if "apy_rate" not in st.session_state:
        st.session_state.apy_rate = 3.0
    if "calendar_sync" not in st.session_state:
        st.session_state.calendar_sync = 0

def savings_window(user_id):
    init_session(user_id)
    current_percentage = st.number_input("Year percentage (%)", value=st.session_state.apy_rate, step=0.1)
    st.session_state.apy_rate = current_percentage
    p_decimal = current_percentage / 100
    tab1, tab2, tab3 = st.tabs(["💰 Add Savings", "📊 Analytics & History", "Withdraw"])
    with tab1:
        target = 5200
        st.progress(st.session_state.balance / target)
        st.write(f"Progress {st.session_state.balance} / {target}UAH")

        suggested = get_daily_suggestion()
        amount = st.number_input("Amount to save today", value=suggested)

        if st.button("Add to Piggy Bank"):
            try:
                feed_piggy_bank(amount, st.session_state.balance + amount, user_id)
                st.session_state.is_deposited = True
                st.session_state.balance += amount
                st.session_state.history = get_savings_history()
                st.session_state.calendar_events = get_calendar_events()
                st.session_state.calendar_sync += 1
                st.balloons()
                st.rerun()
            except sqlite3.IntegrityError:
                st.warning("Hey bro, you made it today. Come back tomorrow :D")
            except sqlite3.Error as e:
                st.error(f"Error of database: {e}")
            except Exception as e:
                st.error(f"Error of system: {e}")
    with tab2:
        if not st.session_state.history.empty:
            st.line_chart(st.session_state.history['balance'])

        col1, col2 = st.columns(2)

        with col1:
            daily = calculate_daily_bonus(st.session_state.balance, p_decimal)
            st.metric("Daily Bonus", f"+{daily:.2f} UAH", delta=f"APY {st.session_state.apy_rate}%")

        with col2:
            monthly = calculate_real_monthly_history(st.session_state.history, p_decimal)
            st.metric("Monthly Forecast", f"+{monthly:.2f} UAH", delta="Passive Income")
        
        st.markdown("### Activity Calendar")

        calendar_options = {
            "initialView": "dayGridMonth",
            "height": 600,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "",
            },
            "selectable": False,
        }

        unique_key = f"calendar_sync_{st.session_state.calendar_sync}"
        calendar(events=st.session_state.calendar_events, options=calendar_options, key=unique_key)
    
    with tab3:
        withdraw_amount = st.number_input("Amount to withdraw", min_value=0.0, max_value=st.session_state.balance)
        is_disabled = not st.session_state.is_deposited
        if is_disabled:
            st.warning("Hey, didn't you forget to put something in the piggy bank first?")

        if st.button("Withdraw money", disabled=is_disabled):
            if withdraw_amount > 0:
                update_savings_entry(-withdraw_amount, user_id)
                st.session_state.balance -= withdraw_amount
                st.session_state.history = get_savings_history(user_id)
                st.session_state.calendar_events = get_calendar_events(user_id)
                st.session_state.calendar_sync += 1
                st.balloons()
                st.rerun()
            else:
                st.info("Enter an amount greater than 0")