from fastapi import FastAPI
import joblib
from typing import List, Dict
from route_optimization import safest_route, alternate_route, G

app = FastAPI()

@app.get("/")
def home():
    return {"message": "NER-SmartRoute API is running. Use /docs to test endpoints."}

# -----------------------------
# Route Endpoint
# -----------------------------
@app.get("/get_route")
def get_route(source: str, target: str):
    source = source.strip().title()
    target = target.strip().title()

    safest = safest_route(G, source, target)
    alternate = alternate_route(G, source, target, safest["route"])

    def decide(route):
        if route["risk_score"] == "HIGH" or route["risk_probability"] > 0.7:
            return "⚠️ Avoid"
        elif route["risk_score"] == "MEDIUM":
            return "Consider"
        else:
            return "✅ Recommended"

    return {
        "routes": [
            {"name": "Route A", **safest, "decision": decide(safest)},
            {"name": "Route B", **alternate, "decision": decide(alternate)}
        ]
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
        return {"risk_level": label_map.get(int(prediction), str(prediction))}
    except Exception as e:
        score = 0
        if rainfall > 3000: score += 1
        if elevation > 1000: score += 1
        if slope > 20: score += 1
        if landslides > 1000: score += 1
        if score >= 3: prediction = "HIGH"
        elif score == 2: prediction = "MEDIUM"
        else: prediction = "LOW"
        return {"risk_level": prediction, "error": str(e)}

# -----------------------------
# Vehicle Tracking
# -----------------------------
vehicle_positions: Dict[str, Dict] = {}

@app.post("/vehicle_tracking")
def vehicle_tracking(vehicle_id: str, latitude: float, longitude: float, timestamp: str):
    vehicle_positions[vehicle_id] = {"latitude": latitude, "longitude": longitude, "timestamp": timestamp}
    return {"status": "updated", "vehicle": vehicle_positions[vehicle_id]}

@app.get("/vehicle_tracking")
def get_vehicle_positions():
    return {"vehicles": vehicle_positions}

@app.get("/get_vehicle_location")
def get_vehicle_location(vehicle_id: str):
    return {"vehicle_id": vehicle_id, "location": vehicle_positions.get(vehicle_id, "Not found")}

# -----------------------------
# Incident Reporting
# -----------------------------
incident_reports: List[Dict] = []

@app.post("/incident_report")
def incident_report(location: str, description: str, severity: str):
    report = {"location": location, "description": description, "severity": severity}
    incident_reports.append(report)
    return {"status": "reported", "incident": report}

@app.get("/incident_report")
def get_incidents():
    return {"incidents": incident_reports}

# -----------------------------
# Alerts
# -----------------------------
@app.get("/alerts")
def get_alerts():
    return {"alerts": [
        {"alert": f"High severity incident at {i['location']}", "details": i}
        for i in incident_reports if i["severity"].upper() in ["HIGH", "CRITICAL"]
    ]}

# -----------------------------
# Road Accessibility
# -----------------------------
@app.get("/road_accessibility")
def road_accessibility(source: str, target: str):
    source = source.strip().title()
    target = target.strip().title()
    safest = safest_route(G, source, target)
    risk = safest.get("risk_score", "UNKNOWN")
    return {"source": source, "target": target, "accessible": risk != "HIGH", "risk_score": risk, "recommended_route": safest}
