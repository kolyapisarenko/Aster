#!/bin/sh

python bot_main.py &

streamlit run main.py --server_port $PORT --server_address 0.0.0.0 -server_headless true