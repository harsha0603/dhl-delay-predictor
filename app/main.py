# ── app/main.py ──────────────────────────────────────────────
# FastAPI backend -- serves the delay prediction model as a REST API
# Architecture: model serving layer decoupled from UI layer
# This API can be consumed by any frontend -- Streamlit, mobile, web
# ─────────────────────────────────────────────────────────────

import pickle
import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

# ── App initialisation ────────────────────────────────────────
app = FastAPI(
    title        = "DHL Delayed Freight Predictor",
    description  = """
    Production REST API for predicting shipment delay days.
    
    Built as part of DHL Data Scientist case study.
    Model: Linear Regression pipeline with preprocessing.
    Features: Origin Region, Carrier, Cargo Type, Weather, 
              Port Congestion, Distance, Planned Month, Day of Week.
    """,
    version      = "1.0.0",
    contact      = {"name": "Harsha", "email": "harsha0461@gmail.com"},
)

# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Load model pipeline ───────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "delay_predictor_pipeline.pkl")

try:
    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    pipeline = None

# ── Input schema ──────────────────────────────────────────────
class ShipmentInput(BaseModel):
    origin_region         : Literal["China", "USA", "Germany", "India", "Brazil"] = Field(..., example="India")
    carrier_name          : Literal["GlobalShip", "OceanWave", "FastLogistics", "AirFreight_Inc", "Unknown"] = Field(..., example="GlobalShip")
    cargo_type            : Literal["Standard", "Perishable", "Hazardous", "Fragile"] = Field(..., example="Perishable")
    weather_index         : int   = Field(..., ge=1, le=10, example=7)
    port_congestion_level : float = Field(..., ge=0.0, le=1.0, example=0.8)
    distance_km           : int   = Field(..., ge=500, le=15000, example=12000)
    planned_month         : int   = Field(..., ge=1, le=12, example=8)
    planned_day_of_week   : int   = Field(..., ge=0, le=6, example=4)

    class Config:
        json_schema_extra = {
            "example": {
                "origin_region"         : "India",
                "carrier_name"          : "GlobalShip",
                "cargo_type"            : "Perishable",
                "weather_index"         : 7,
                "port_congestion_level" : 0.8,
                "distance_km"           : 12000,
                "planned_month"         : 8,
                "planned_day_of_week"   : 4
            }
        }

# ── Output schema ─────────────────────────────────────────────
class PredictionOutput(BaseModel):
    predicted_delay_days  : float
    risk_level            : str
    risk_colour           : str
    business_message      : str
    model_version         : str

# ── Helper functions ──────────────────────────────────────────
def classify_risk(delay_days: float) -> tuple:
    """Classify delay into risk levels for business communication."""
    if delay_days <= 2:
        return "LOW", "#2ECC71", "Shipment is expected to arrive close to schedule. No intervention required."
    elif delay_days <= 6:
        return "MEDIUM", "#F39C12", "Moderate delay expected. Consider notifying the customer proactively."
    else:
        return "HIGH", "#E74C3C", "Significant delay expected. Immediate intervention recommended -- consider expedited routing or customer escalation."

def build_input_df(data: ShipmentInput) -> pd.DataFrame:
    """Convert API input to DataFrame matching training feature format."""
    return pd.DataFrame([{
        "Origin_Region"         : data.origin_region,
        "Carrier_Name"          : data.carrier_name,
        "Cargo_Type"            : data.cargo_type,
        "Weather_Index"         : data.weather_index,
        "Port_Congestion_Level" : data.port_congestion_level,
        "Distance_KM"           : data.distance_km,
        "Planned_Month"         : data.planned_month,
        "Planned_DayOfWeek"     : data.planned_day_of_week,
    }])

# ── Routes ────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint -- confirms API and model are running."""
    return {
        "status"       : "healthy",
        "model_loaded" : pipeline is not None,
        "api_version"  : "1.0.0"
    }

@app.post("/predict", response_model=PredictionOutput, tags=["Prediction"])
def predict_delay(shipment: ShipmentInput):
    """
    Predict the number of delay days for a shipment.
    
    Takes shipment details and returns:
    - Predicted delay in days
    - Risk classification (LOW / MEDIUM / HIGH)
    - Business recommendation
    """
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Check server logs.")

    try:
        # Build input DataFrame
        input_df = build_input_df(shipment)

        # Run prediction through pipeline
        # Pipeline handles encoding and scaling internally
        prediction = pipeline.predict(input_df)[0]
        prediction = round(float(prediction), 2)

        # Classify risk
        risk_level, risk_colour, business_message = classify_risk(prediction)

        return PredictionOutput(
            predicted_delay_days = prediction,
            risk_level           = risk_level,
            risk_colour          = risk_colour,
            business_message     = business_message,
            model_version        = "1.0.0 -- Linear Regression Pipeline"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.get("/", tags=["System"])
def root():
    """Root endpoint -- API information."""
    return {
        "message"     : "DHL Delayed Freight Predictor API",
        "version"     : "1.0.0",
        "docs"        : "/docs",
        "health"      : "/health",
        "predict"     : "/predict"
    }
    