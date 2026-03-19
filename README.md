# DHL Delayed Freight Predictor

Predicts shipment delay days using a machine learning pipeline.
Built as part of DHL Data Scientist case study.

## Architecture
```
FastAPI Backend  (port 8000)  -->  serves the ML model as REST API
Streamlit Frontend (port 8501) -->  UI that calls the API
```

Decoupled architecture -- the model serving layer is independent
of the presentation layer. Any frontend can consume the API.

## Running Locally (without Docker)

### Step 1 -- Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### Step 2 -- Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 -- Start FastAPI backend
```bash
uvicorn app.main:app --reload
```
API runs at: http://127.0.0.1:8000
API docs at: http://127.0.0.1:8000/docs

### Step 4 -- Start Streamlit (new terminal)
```bash
streamlit run streamlit_app.py
```
Dashboard at: http://localhost:8501

## Running with Docker

### Prerequisites
- Docker Desktop installed and running

### One command to run everything
```bash
docker-compose up --build
```

- API:       http://localhost:8000
- API Docs:  http://localhost:8000/docs
- Dashboard: http://localhost:8501

### Stop everything
```bash
docker-compose down
```

## API Endpoints

| Endpoint  | Method | Description                    |
|-----------|--------|--------------------------------|
| /         | GET    | API information                |
| /health   | GET    | Health check                   |
| /predict  | POST   | Predict delay for a shipment   |
| /docs     | GET    | Interactive API documentation  |

## Project Structure
```
DHL_Delay_Predictor/
├── app/
│   ├── __init__.py
│   ├── main.py                          -- FastAPI backend
│   └── model/
│       └── delay_predictor_pipeline.pkl -- Trained ML pipeline
├── streamlit_app.py                     -- Streamlit frontend
├── requirements.txt                     -- Dependencies
├── Dockerfile                           -- Container definition
├── docker-compose.yml                   -- Multi-service orchestration
├── start.sh                             -- Startup script
└── README.md                            -- This file
```

## Model Details

- Algorithm: Linear Regression Pipeline
- Features: Origin Region, Carrier, Cargo Type, Weather Index,
            Port Congestion Level, Distance KM, Planned Month,
            Planned Day of Week
- Target: Delay Days (-2 to 10 days)
- Preprocessing: OneHotEncoder + StandardScaler inside pipeline

## Tech Stack

- FastAPI -- REST API framework
- Streamlit -- Interactive dashboard
- scikit-learn -- ML pipeline
- XGBoost -- Gradient boosting (trained, compared)
- Docker -- Containerisation
- Pydantic -- Input validation
```