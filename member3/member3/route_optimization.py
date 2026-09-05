import pandas as pd
import networkx as nx
import json

# -----------------------------
# 1. Load datasets
# -----------------------------
roads = pd.read_csv("member6_ml_ready_with_slope.csv")
risk = pd.read_csv("district_risk_predictions.csv")

# Merge risk scores into road dataset
roads = roads.merge(risk[["district_name", "risk_level"]],
                    on="district_name", how="left")

# -----------------------------
# 2. Build road network graph
# -----------------------------
G = nx.Graph()

# Connect each district to its state hub
for _, row in roads.iterrows():
    risk_weight = {"LOW": 1, "MEDIUM": 1.5, "HIGH": 3}[row["risk_level"]]

    distance_km = max(1, row["slope_deg"])   # slope as proxy for distance
    travel_time_min = distance_km * 2        # assume 2 min per km

    G.add_edge(row["district_name"],
               row["state_name"],
               weight=distance_km * risk_weight,
               distance_km=distance_km,
               travel_time_min=travel_time_min,
               risk=row["risk_level"])

# Connect all states to each other (simplified national graph)
states = roads["state_name"].unique()
for i, s1 in enumerate(states):
    for s2 in states[i+1:]:
        avg_risk = roads[roads["state_name"] == s2]["risk_level"].mode()[0]
        risk_weight = {"LOW": 1, "MEDIUM": 1.5, "HIGH": 3}[avg_risk]

        G.add_edge(s1, s2,
                   weight=10 * risk_weight,
                   distance_km=10,
                   travel_time_min=20,
                   risk=avg_risk)

# -----------------------------
# 3. Route functions
# -----------------------------
def safest_route(G, source, target):
    path = nx.shortest_path(G, source, target, weight="weight")
    return format_route(G, path)

def alternate_route(G, source, target, safest_path):
    for u, v in zip(safest_path[:-1], safest_path[1:]):
        if G.has_edge(u, v):
            G[u][v]["weight"] *= 5  # penalize safest path edges
    path = nx.shortest_path(G, source, target, weight="weight")
    return format_route(G, path)

def format_route(G, path):
    distance = 0
    time = 0
    risks = []
    for u, v in zip(path[:-1], path[1:]):
        edge = G[u][v]
        distance += edge["distance_km"]
        time += edge["travel_time_min"]
        risks.append(edge["risk"])
    risk_priority = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    risk_score = max(risks, key=lambda r: risk_priority[r])
    return {
        "route": path,
        "distance_km": round(distance, 2),
        "travel_time_min": round(time, 2),
        "risk_score": risk_score
    }
