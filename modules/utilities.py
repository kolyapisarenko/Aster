from utils.database import get_latest_metrics, save_utility_record
from models.UtilityRecord import UtilityRecord
import pandas as pd
import streamlit as st

    
def get_detailed_report(report: UtilityRecord):
    used_day = report.curr_reading_day - report.prev_reading_day
    used_night = report.curr_reading_night - report.prev_reading_night

    match report.service_type:
        case "Electricity":
            data = {
                "Current" : [report.curr_reading_day, report.curr_reading_night, ""],
                "Previous" : [report.prev_reading_day, report.prev_reading_night, ""],
                "Consumed" : [used_day, used_night, ""],
                "Tariff" : [report.tariff_day, report.tariff_night, ""],
                "Sum" : [used_day * report.tariff_day, used_night * report.tariff_night, report.total_to_pay]
            }
            index = ["Day", "Night", "Together"]
        case "Water":
            data = {
                "Current" : [report.curr_reading_day, "", ""],
                "Previous" : [report.prev_reading_day, "", ""],
                "Consumed" : [used_day, "", ""],
                "Tariff" : [report.tariff_day, "", ""],
                "Sum": [used_day * report.tariff_day, report.water_constant, report.total_to_pay]
            }
            index = ["For the month", "Fixed fee", "Together"]
        case "Gas":
            data = {
                "Records" : [report.curr_reading_day, report.prev_reading_day, used_day],
                "Money" : [f"Tariff {report.tariff_day}", f"Sum {report.total_to_pay}", ""]
            }
            index = ["Current", "Previous", "Consumed"]
    return pd.DataFrame(data, index=index)

def utility_report_window(user_id):
    st.set_page_config(page_title="Aster Utility Tracker", page_icon="⚡")
    st.title("Aster: Utility Assistant")

    st.sidebar.header("Navigation")
    selected_service = st.sidebar.selectbox(
        "Select Service",
        ["Electricity", "Water", "Gas"]
    )
    old_data = get_latest_metrics(selected_service, user_id)

    st.subheader(f"New entry for {selected_service}")
    with st.form("utility_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Day / Main readings**")
            prev_day = st.number_input("Previous", value=float(old_data[0]), disabled=True)
            curr_day = st.number_input("Current", min_value=prev_day, step=1.0)
            t_day = st.number_input("Tariff (Day)", value=float(old_data[2]), step=0.01)

        with col2:
            if selected_service == "Electricity":
                st.write("**Night readings**")
                prev_night = st.number_input("Previous (Night)", value=float(old_data[1]), disabled=True)
                curr_night = st.number_input("Current (Night)", min_value=prev_night, step=1.0)
                t_night = st.number_input("Tariff (Night)", value=float(old_data[3]), step=0.01)
            else:
                curr_night, t_night = 0.0, 0.0
                st.info(f"Night metrics are not used for {selected_service}")

        water_const = 0.0
        if selected_service == "Water":
            water_const = st.number_input("Fixed Fee / Constant", value=36.0, step=0.5)

        submit = st.form_submit_button("Calculate & Preview")

    if submit:
        record = UtilityRecord(
            service_type=selected_service,
            prev_reading_day=prev_day,
            curr_reading_day=curr_day,
            tariff_day=t_day,
            water_constant=water_const,
            prev_reading_night=prev_night if selected_service == "Electricity" else 0,
            curr_reading_night=curr_night if selected_service == "Electricity" else 0,
            tariff_night=t_night
        )
        report = get_detailed_report(record)

        st.success(f"Calculation complete! Total to pay: {record.total_to_pay:.2f} UAH")
        st.table(report)
        st.session_state["current_record"] = record
        
    if st.button("Save to Database"):
        save_utility_record(st.session_state["current_record"], user_id)
        st.balloons()
        st.write("Data saved successfully!")
        del st.session_state['current_record']