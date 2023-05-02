#!/bin/bash
apt-get update
apt-get install -y libssl-dev libasound2
python -m streamlit run app/app.py --server.port 8000 --server.address 0.0.0.0