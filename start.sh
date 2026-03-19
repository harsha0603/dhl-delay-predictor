#!/bin/bash
# Start FastAPI backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend in foreground
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0