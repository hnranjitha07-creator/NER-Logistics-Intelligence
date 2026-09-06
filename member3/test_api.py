import requests

BASE_URL = "http://127.0.0.1:8000"

def check_endpoint(name, url, method="GET", params=None):
    try:
        if method == "GET":
            r = requests.get(url, params=params)
        else:
            r = requests.post(url, params=params)
        if r.status_code == 200:
            print(f"✅ {name} OK | Input: {params}")
            print(r.json())
        else:
            print(f"❌ {name} FAILED ({r.status_code}) | Input: {params}")
    except Exception as e:
        print(f"❌ {name} ERROR: {e} | Input: {params}")

# --- Predict Risk ---
print("\n--- Predict Risk ---")
rainfall = float(input("Enter rainfall: "))
elevation = float(input("Enter elevation: "))
slope = float(input("Enter slope: "))
landslides = int(input("Enter landslides: "))

check_endpoint("Predict Risk", f"{BASE_URL}/predict_risk", "POST",
               {"rainfall": rainfall, "elevation": elevation, "slope": slope, "landslides": landslides})

# --- Get Route ---
print("\n--- Get Route ---")
source = input("Enter source district: ")
target = input("Enter target district: ")

check_endpoint("Get Route", f"{BASE_URL}/get_route", "GET",
               {"source": source, "target": target})

# --- Road Accessibility ---
print("\n--- Road Accessibility ---")
check_endpoint("Road Accessibility", f"{BASE_URL}/road_accessibility", "GET",
               {"source": source, "target": target})

# --- Incident Report ---
print("\n--- Incident Report ---")
location = input("Enter incident location: ")
description = input("Enter incident description: ")
severity = input("Enter severity (LOW/MEDIUM/HIGH): ")

check_endpoint("Incident Report", f"{BASE_URL}/incident_report", "POST",
               {"location": location, "description": description, "severity": severity})

# --- Alerts ---
print("\n--- Alerts ---")
check_endpoint("Alerts", f"{BASE_URL}/alerts")

# --- Vehicle Tracking ---
print("\n--- Vehicle Tracking ---")
vehicle_id = input("Enter vehicle ID: ")
latitude = float(input("Enter latitude: "))
longitude = float(input("Enter longitude: "))
timestamp = input("Enter timestamp (YYYY-MM-DDTHH:MM:SS): ")

check_endpoint("Vehicle Tracking", f"{BASE_URL}/vehicle_tracking", "POST",
               {"vehicle_id": vehicle_id, "latitude": latitude, "longitude": longitude, "timestamp": timestamp})

print("\n--- Get Vehicle Location ---")
check_endpoint("Get Vehicle Location", f"{BASE_URL}/get_vehicle_location", "GET",
               {"vehicle_id": vehicle_id})
