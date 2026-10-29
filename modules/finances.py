import json
import base64
import streamlit as st
import pandas as pd
from pathlib import Path

DATA_PATH = Path("./data")
currencies = pd.read_csv(DATA_PATH / "currency.csv")
currencies = currencies.dropna()
currencies = currencies.drop_duplicates(keep="first", subset=["Code"])
currencies["Symbol and Code"] = currencies["Symbol"] + "\n" + currencies["Code"]

with open(DATA_PATH / "transaction_categories.json", "r", encoding="utf-8") as tc:
    all_categories = json.load(tc)

income_list = all_categories["income"]
spend_list = all_categories["expenses"]

def finance_window():
    st.markdown("""
        <style>
        .custom-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(49, 51, 63, 0.2);
            background-color: var(--background-color);
            transition: all 0.25s ease-in-out;
            cursor: pointer;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .custom-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
            border-color: #ff4b4b;
        }
        </style>
    """, unsafe_allow_html=True)
    
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
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    for i in range(0, len(category_target_list), 3):
        cols = st.columns(3)
        for col, category in zip(cols, category_target_list[i:i + 3]):
            with col:
                img_path = PROJECT_ROOT / "assets" / "svg" / f"{category['id']}.svg"
                
                svg_src = ""
                if img_path.exists():
                    encoded_svg = base64.b64encode(img_path.read_bytes()).decode("utf-8")
                    svg_src = f"data:image/svg+xml;base64,{encoded_svg}"
                
                st.markdown(f"""
                    <div class="custom-card">
                        <div style="width: 64px; height: 64px; margin-bottom: 8px; display: flex; justify-content: center; align-items: center;">
                            <img src="{svg_src}" width="64" style="max-height: 64px; object-fit: contain;" />
                        </div>
                        <div style="font-weight: 600; font-size: 14px;">{category['name']}</div>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    finance_window()