# ── streamlit_app.py ─────────────────────────────────────────
# Streamlit frontend -- consumes the FastAPI backend
# UI layer is completely decoupled from model serving layer
# This app calls POST /predict on the FastAPI backend
# ─────────────────────────────────────────────────────────────

import streamlit as st
import requests
import json

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title = "DHL Delay Predictor",
    page_icon  = "🚚",
    layout     = "wide",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        background-color: #FFCC00;
        color: #000000;
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px;
        padding: 12px 40px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #e6b800;
        color: #000000;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .risk-high   { color: #E74C3C; font-size: 32px; font-weight: bold; }
    .risk-medium { color: #F39C12; font-size: 32px; font-weight: bold; }
    .risk-low    { color: #2ECC71; font-size: 32px; font-weight: bold; }
    .header-style {
        background: linear-gradient(135deg, #FFCC00, #FF6B00);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="header-style">
    <h1 style="color:black; margin:0;">🚚 DHL Delayed Freight Predictor</h1>
    <p style="color:black; margin:5px 0 0 0;">
        Enter shipment details to predict delay days and get a risk assessment
    </p>
</div>
""", unsafe_allow_html=True)

# ── API config ────────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000/predict"

# ── Layout ────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📦 Shipment Details")

    origin_region = st.selectbox(
        "Origin Region",
        ["China", "USA", "Germany", "India", "Brazil"],
        help="Country of origin for the shipment"
    )

    carrier_name = st.selectbox(
        "Carrier Name",
        ["GlobalShip", "OceanWave", "FastLogistics", "AirFreight_Inc", "Unknown"],
        help="Logistics carrier handling the shipment"
    )

    cargo_type = st.selectbox(
        "Cargo Type",
        ["Standard", "Perishable", "Hazardous", "Fragile"],
        help="Type of cargo being shipped"
    )

    distance_km = st.slider(
        "Distance (KM)",
        min_value  = 500,
        max_value  = 15000,
        value      = 7500,
        step       = 100,
        help       = "Total shipping distance in kilometres"
    )

with col2:
    st.subheader("🌍 Route Conditions")

    weather_index = st.slider(
        "Weather Index",
        min_value = 1,
        max_value = 10,
        value     = 5,
        step      = 1,
        help      = "Weather severity (1 = clear, 10 = severe)"
    )

    port_congestion = st.slider(
        "Port Congestion Level",
        min_value = 0.0,
        max_value = 1.0,
        value     = 0.5,
        step      = 0.01,
        help      = "Port congestion level (0 = clear, 1 = fully congested)"
    )

    planned_month = st.selectbox(
        "Planned Month",
        options    = list(range(1, 13)),
        index      = 0,
        format_func= lambda x: [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ][x-1],
        help = "Month the shipment is planned"
    )

    planned_day = st.selectbox(
        "Planned Day of Week",
        options     = list(range(7)),
        format_func = lambda x: ["Monday","Tuesday","Wednesday",
                                  "Thursday","Friday","Saturday","Sunday"][x],
        help = "Day of week the shipment is planned"
    )

# ── Predict button ────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
predict_clicked = st.button("🔮 Predict Delay")

if predict_clicked:
    # Build payload
    payload = {
        "origin_region"         : origin_region,
        "carrier_name"          : carrier_name,
        "cargo_type"            : cargo_type,
        "weather_index"         : weather_index,
        "port_congestion_level" : port_congestion,
        "distance_km"           : distance_km,
        "planned_month"         : planned_month,
        "planned_day_of_week"   : planned_day
    }

    with st.spinner("Calling prediction API..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()

                st.markdown("---")
                st.subheader("📊 Prediction Results")

                # ── Result cards ──────────────────────────────
                r1, r2, r3 = st.columns(3)

                with r1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <p style="color:gray; margin:0;">Predicted Delay</p>
                        <h2 style="margin:8px 0; color:#1a1a1a;">
                            {result['predicted_delay_days']} days
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)

                with r2:
                    risk    = result['risk_level']
                    colour  = result['risk_colour']
                    st.markdown(f"""
                    <div class="metric-card">
                        <p style="color:gray; margin:0;">Risk Level</p>
                        <h2 style="margin:8px 0; color:{colour};">
                            {risk}
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)

                with r3:
                    delay = result['predicted_delay_days']
                    on_time_prob = max(0, min(100, int((10 - delay) / 12 * 100)))
                    st.markdown(f"""
                    <div class="metric-card">
                        <p style="color:gray; margin:0;">On-Time Probability</p>
                        <h2 style="margin:8px 0; color:#3498DB;">
                            {on_time_prob}%
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Business recommendation ───────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                colour = result['risk_colour']
                msg    = result['business_message']
                risk   = result['risk_level']

                st.markdown(f"""
                <div style="background:{colour}22; border-left: 5px solid {colour};
                     padding:16px 20px; border-radius:8px;">
                    <strong style="color:{colour};">
                        {'⚠️' if risk=='HIGH' else '📌' if risk=='MEDIUM' else '✅'}
                        Business Recommendation
                    </strong><br>
                    <span style="color:#ffffff;">{msg}</span>
                </div>
                """, unsafe_allow_html=True)

                # ── Input summary ─────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📋 View Input Summary"):
                    summary_df = {
                        "Feature" : list(payload.keys()),
                        "Value"   : [str(v) for v in payload.values()]
                    }
                    st.table(summary_df)

                # ── API response ──────────────────────────────
                with st.expander("🔌 Raw API Response (JSON)"):
                    st.json(result)

            else:
                st.error(f"API Error {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("""
            ❌ Cannot connect to FastAPI backend.
            Make sure the API is running:
            uvicorn app.main:app --reload
            """)
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:gray; font-size:12px;">
    DHL Delayed Freight Predictor  •  Built by Harsha  •  
    Model: Linear Regression Pipeline  •  
    Architecture: FastAPI + Streamlit
</div>
""", unsafe_allow_html=True)