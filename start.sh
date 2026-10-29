#!/bin/sh

python -u bot_main.py &

streamlit run main.py --server.port $PORT --server.address 0.0.0.0 --server.headless true