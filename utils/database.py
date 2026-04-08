import sqlite3
import os
from datetime import date, datetime
import pandas as pd
from models.UtilityRecord import UtilityRecord

DB_PATH = os.getenv("DB_PATH", os.path.join("data", "aster_database.db"))

def get_connection():
    return sqlite3.connect(DB_PATH)

def execute_query(query, params=(), fetch=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch and fetch.lower() == "all":
            return cursor.fetchall()
        if fetch and fetch.lower() == "one":
            return cursor.fetchone()
        conn.commit()

# --- UTILITIES ---

def create_utility_table():
    query = """
    CREATE TABLE IF NOT EXISTS utilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        service_type TEXT NOT NULL CHECK(service_type IN ('Electricity', 'Water', 'Gas')),
        prev_reading_day REAL DEFAULT 0,
        curr_reading_day REAL NOT NULL,
        tariff_day REAL NOT NULL,
        prev_reading_night REAL DEFAULT 0,
        curr_reading_night REAL DEFAULT 0,
        tariff_night REAL DEFAULT 0,
        total_to_pay REAL DEFAULT 0.0,
        date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    execute_query(query)

def get_latest_metrics(service_name, user_id):
    query = """
    SELECT curr_reading_day, curr_reading_night, tariff_day, tariff_night 
    FROM utilities 
    WHERE service_type = ? AND user_id = ? 
    ORDER BY id DESC LIMIT 1
    """
    row = execute_query(query, (service_name, user_id), "one")
    return row if row else (0, 0, 0, 0)

def save_utility_record(record: UtilityRecord, user_id):
    query = """
    INSERT INTO utilities (
        user_id, service_type, prev_reading_day, curr_reading_day, tariff_day,
        prev_reading_night, curr_reading_night, tariff_night, total_to_pay, date_recorded
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params = (
        user_id, record.service_type, record.prev_reading_day, record.curr_reading_day, 
        record.tariff_day, record.prev_reading_night, record.curr_reading_night, 
        record.tariff_night, record.total_to_pay, now
    )
    execute_query(query, params)

def get_utility_history(service_name, user_id, limit=10):
    query = "SELECT * FROM utilities WHERE service_type = ? AND user_id = ? ORDER BY date_recorded DESC LIMIT ?"
    return execute_query(query, (service_name, user_id, limit), "all")

# --- SAVINGS ---

def create_saving_table():
    query = """
    CREATE TABLE IF NOT EXISTS savings(
        user_id INTEGER NOT NULL,
        event_date DATE NOT NULL,
        amount INT NOT NULL,
        balance_at_moment REAL NOT NULL,
        PRIMARY KEY (user_id, event_date)
    )
    """
    execute_query(query)

def feed_piggy_bank(amount, balance, user_id):
    query = "INSERT INTO savings (user_id, event_date, amount, balance_at_moment) VALUES (?, ?, ?, ?)"
    params = (user_id, date.today().isoformat(), amount, balance)
    execute_query(query, params)

def get_current_balance(user_id):
    query = "SELECT balance_at_moment FROM savings WHERE user_id = ? ORDER BY event_date DESC LIMIT 1"
    row = execute_query(query, (user_id,), fetch="one")
    return row[0] if row else 0.0

def get_savings_history(user_id):
    query = "SELECT event_date, balance_at_moment FROM savings WHERE user_id = ? ORDER BY event_date ASC"
    rows = execute_query(query, (user_id,), fetch="all")
    return pd.DataFrame(rows, columns=['date', 'balance']).set_index('date')

def get_calendar_events(user_id):
    query = "SELECT event_date, amount FROM savings WHERE user_id = ?"
    rows = execute_query(query, (user_id,), fetch="all")
    events = []
    for row in rows:
        color = "#28a745" if row[1] > 0 else "#dc3545"
        events.append({
            "title": f"Saved {row[1]}₴",
            "start": row[0],
            "allDay": True,
            "backgroundColor": color,
            "borderColor": color
        })
    return events

def get_current_savings(user_id):
    query = "SELECT amount, balance_at_moment FROM savings WHERE user_id = ? ORDER BY event_date DESC LIMIT 1"
    row = execute_query(query, (user_id,), fetch="one")
    return row if row else (0, 0.0)

def update_savings_entry(amount, user_id):
    curr_amount, curr_balance = get_current_savings(user_id)
    query = "UPDATE savings SET amount = ?, balance_at_moment = ? WHERE event_date = ? AND user_id = ?"
    new_amount = curr_amount + amount
    params = (new_amount, curr_balance + amount, date.today().isoformat(), user_id)
    execute_query(query, params)

# --- HABITS ---

def create_habit_tables():
    habit_query = """
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        freq_type TEXT NOT NULL,
        freq_value TEXT,
        start_date DATE NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at DATE DEFAULT (date('now')),
        UNIQUE(user_id, name)
    )
    """
    habit_log = """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        habit_id INTEGER NOT NULL,
        log_date DATE DEFAULT (date('now')),
        status INTEGER DEFAULT 0,
        FOREIGN KEY (habit_id) REFERENCES habits (id),
        UNIQUE(user_id, habit_id, log_date)
    )
    """
    execute_query(habit_query)
    execute_query(habit_log)

def add_habit(name, f_type, value, start_dt, user_id):
    query = "INSERT INTO habits (user_id, name, freq_type, freq_value, start_date, created_at) VALUES (?, ?, ?, ?, ?, ?)"
    params = (user_id, name, f_type, value, start_dt, date.today().isoformat())
    execute_query(query, params)

def log_habit(habit_id, log_date, status, user_id):
    query = "INSERT OR REPLACE INTO habit_logs (user_id, habit_id, log_date, status) VALUES(?, ?, ?, ?)"
    params = (user_id, habit_id, log_date, status)
    execute_query(query, params)

def get_habits_for_today(target_date, user_id):
    query = """
        SELECT h.id, h.name, h.freq_type, h.freq_value, h.start_date, COALESCE(l.status, 0) as status 
        FROM habits h 
        LEFT JOIN habit_logs l on h.id = l.habit_id AND l.log_date = ? AND l.user_id = ?
        WHERE h.is_active = 1 AND h.user_id = ?
    """
    all_habits = execute_query(query, (target_date, user_id, user_id), fetch="all")
    filtered_habits = []

    for habit in all_habits:
        h_id, name, f_type, f_value, start_date_str, status = habit
        start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if is_habit_scheduled(target_date, f_type, f_value, start_dt):
            filtered_habits.append((h_id, name, status))

    return filtered_habits

def delete_habit(habit_id, user_id):
    query = "UPDATE habits SET is_active = 0 WHERE id = ? AND user_id = ?"
    execute_query(query, (habit_id, user_id))

def get_all_habits(user_id):
    query = "SELECT id, name FROM habits WHERE is_active = 1 AND user_id = ?"
    return execute_query(query, (user_id,), fetch="all")

def get_habit_total_count(habit_id, user_id):
    query = "SELECT COUNT(*) FROM habit_logs WHERE habit_id = ? AND status = 1 AND user_id = ?"
    result = execute_query(query, (habit_id, user_id), fetch="one")
    return result[0] if result else 0

def get_done_dates(habit_id, user_id):
    query = "SELECT log_date FROM habit_logs WHERE habit_id = ? AND status = 1 AND user_id = ?"
    result = execute_query(query, (habit_id, user_id), fetch="all")
    return {row[0] for row in result} if result else set()

def get_habit_data(h_id, user_id):
    query = "SELECT freq_type, freq_value, start_date FROM habits WHERE id = ? AND user_id = ?"
    result = execute_query(query, (h_id, user_id), fetch="one")
    return result if result else None

# --- SHARED ---

def is_habit_scheduled(target_date, f_type, f_value, start_date):
    if target_date < start_date:
        return False    
    if f_type == "Daily":
        return True
    elif f_type == "Weekdays":
        return target_date.weekday() < 5
    elif f_type == "Weekends":
        return target_date.weekday() > 4
    elif f_type == "Custom Interval":
        delta = (target_date - start_date).days
        return delta % int(f_value) == 0
    elif f_type == "Specific Days":
        return str(target_date.weekday()) in f_value.split(',')
    return False

def init_db():
    create_utility_table()
    create_saving_table()
    create_habit_tables()