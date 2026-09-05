from fastapi import FastAPI
import joblib
import pandas as pd
from route_optimization import safest_route, alternate_route, G   # Member 4's file
from typing import List, Dict

app = FastAPI()

# -----------------------------
# Homepage Route
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "NER-SmartRoute API is running. Use /docs to test endpoints."
    }

# -----------------------------
# Route Endpoint
# -----------------------------
@app.post("/get_route")
def get_route(source: str, target: str):
    # Normalize inputs to match CSV entries
    source = source.strip().title()
    target = target.strip().title()

    safest = safest_route(G, source, target)
    alternate = alternate_route(G, source, target, safest["route"])
    return {
        "recommended_route": safest,
        "alternate_route": alternate
    }

# -----------------------------
# Risk Prediction Endpoint
# -----------------------------
@app.post("/predict_risk")
def predict_risk(rainfall: float, elevation: float, slope: float, landslides: int):
    try:
        model = joblib.load("risk_model.pkl")
        features = [[rainfall, elevation, slope, landslides]]
        prediction = model.predict(features)[0]

        label_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
        risk_label = label_map.get(int(prediction), str(prediction))

        return {"risk_level": risk_label}

    except Exception as e:
        score = 0
        if rainfall > 3000: score += 1
        if elevation > 1000: score += 1
        if slope > 20: score += 1
        if landslides > 1000: score += 1

        if score >= 3:
            prediction = "HIGH"
        elif score == 2:
            prediction = "MEDIUM"
        else:
            prediction = "LOW"

        return {
            "risk_level": prediction,
            "error": str(e),
            "inputs": {
                "rainfall": rainfall,
                "elevation": elevation,
                "slope": slope,
                "landslides": landslides
            }
        }

# -----------------------------
# Vehicle Tracking Endpoint
# -----------------------------
vehicle_positions: Dict[str, Dict] = {}

@app.post("/vehicle_tracking")
def vehicle_tracking(vehicle_id: str, latitude: float, longitude: float, timestamp: str):
    vehicle_positions[vehicle_id] = {
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp
    }
    return {"status": "updated", "vehicle": vehicle_positions[vehicle_id]}

@app.get("/vehicle_tracking")
def get_vehicle_positions():
    return {"vehicles": vehicle_positions}

# NEW: Get single vehicle location
@app.get("/get_vehicle_location")
def get_vehicle_location(vehicle_id: str):
    if vehicle_id in vehicle_positions:
        return {"vehicle_id": vehicle_id, "location": vehicle_positions[vehicle_id]}
    return {"error": "Vehicle not found"}

# -----------------------------
# Incident Reporting Endpoint
# -----------------------------
incident_reports: List[Dict] = []

@app.post("/incident_report")
def incident_report(location: str, description: str, severity: str):
    report = {
        "location": location,
        "description": description,
        "severity": severity
    }
    incident_reports.append(report)
    return {"status": "reported", "incident": report}

@app.get("/incident_report")
def get_incidents():
    return {"incidents": incident_reports}

# -----------------------------
# Alerts Endpoint
# -----------------------------
@app.get("/alerts")
def get_alerts():
    alerts = []
    for incident in incident_reports:
        if incident["severity"].upper() in ["HIGH", "CRITICAL"]:
            alerts.append({
                "alert": f"High severity incident at {incident['location']}",
                "details": incident
            })
    return {"alerts": alerts}

# -----------------------------
# Road Accessibility Endpoint
# -----------------------------
@app.get("/road_accessibility")
def road_accessibility(source: str, target: str):
    # Normalize inputs to match CSV entries
    source = source.strip().title()
    target = target.strip().title()

    safest = safest_route(G, source, target)
    risk = safest.get("risk_score", "UNKNOWN")
    accessible = risk != "HIGH"
    return {
        "source": source,
        "target": target,
        "accessible": accessible,
        "risk_score": risk,
        "recommended_route": safest
    }
