import json
import streamlit as st
import pandas as pd
from pathlib import Path

DATA_PATH = Path("./data")
currencies = pd.read_csv(DATA_PATH / "currency.csv")
currencies = currencies.dropna()
currencies = currencies.drop_duplicates(keep="first", subset=["Code"])
currencies["Symbol and Code"] = currencies["Symbol"] + " - " + currencies["Code"]

with open(DATA_PATH / "transaction_categories.json", "r", encoding="utf-8") as tc:
    all_categories = json.load(tc)

income_list = all_categories["income"]
spend_list = all_categories["expenses"]

def finance_window():
    st.caption("TOTAL BALANCE")

    col_balance, col_currency, col_empty = st.columns([2, 1.5, 3])

    with col_balance:
        st.markdown(
            "<h1 style='margin:0; padding:0; line-height:1;'>0</h1>",
            unsafe_allow_html=True,
        )

    with col_currency:
        currency_to_display = st.selectbox(
            options=currencies["Symbol and Code"],
            label="Select currency",
            label_visibility="collapsed",
        )
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    col_amount, col_type, col_empty = st.columns([2, 1.5, 3])
    with col_amount:
        st.number_input("", min_value=0)
    with col_type:
        transaction_type = st.selectbox("Select transaction type", ["Income", "Spend"])

    st.button("Add")
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    st.caption("Select category")

    category_target_list = income_list if transaction_type == "Income" else spend_list

    for i in range(0, len(category_target_list), 3):
        cols = st.columns(3)

        for col, category in zip(cols, category_target_list[i:i + 3]):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{category['name']}**")

if __name__ == "__main__":
    finance_window()