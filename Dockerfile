# ── Dockerfile ───────────────────────────────────────────────
# Multi-service container for DHL Delay Predictor
# Runs both FastAPI backend and Streamlit frontend
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Set working directory
WORKDIR /app_root

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY streamlit_app.py .

# Expose ports
# 8000 = FastAPI
# 8501 = Streamlit
EXPOSE 8000
EXPOSE 8501

# Start both services using a shell script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]