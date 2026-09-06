import pandas as pd
import networkx as nx

roads = pd.read_csv("member6_ml_ready_with_slope.csv")
risk = pd.read_csv("district_risk_predictions.csv")

roads = roads.merge(
    risk[["district_name", "risk_level", "risk_probability"]],
    on="district_name", how="left"
)

# Fill missing values
roads["risk_level"] = roads["risk_level"].fillna("LOW")
roads["risk_probability"] = roads["risk_probability"].fillna(0.0)

G = nx.Graph()

for _, row in roads.iterrows():
    risk_weight = {"LOW": 1, "MEDIUM": 1.5, "HIGH": 3}[row["risk_level"]]
    distance_km = max(1, row["slope_deg"])
    travel_time_min = distance_km * 2

    G.add_edge(
        row["district_name"],
        row["state_name"],
        weight=distance_km * risk_weight,
        distance_km=distance_km,
        travel_time_min=travel_time_min,
        risk=row["risk_level"],
        risk_probability=float(row["risk_probability"])
    )

states = roads["state_name"].unique()
for i, s1 in enumerate(states):
    for s2 in states[i+1:]:
        avg_risk = roads[roads["state_name"] == s2]["risk_level"].mode()[0]
        avg_prob = roads[roads["state_name"] == s2]["risk_probability"].mean()
        risk_weight = {"LOW": 1, "MEDIUM": 1.5, "HIGH": 3}[avg_risk]

        G.add_edge(
            s1, s2,
            weight=10 * risk_weight,
            distance_km=10,
            travel_time_min=20,
            risk=avg_risk,
            risk_probability=float(avg_prob)
        )

def safest_route(G, source, target):
    try:
        path = nx.shortest_path(G, source, target, weight="weight")
        return format_route(G, path)
    except nx.NodeNotFound:
        return {"error": f"Node not found: {source} or {target}"}
    except nx.NetworkXNoPath:
        return {"error": f"No route found between {source} and {target}"}

def alternate_route(G, source, target, safest_path):
    try:
        for u, v in zip(safest_path[:-1], safest_path[1:]):
            if G.has_edge(u, v):
                G[u][v]["weight"] *= 5
        path = nx.shortest_path(G, source, target, weight="weight")
        return format_route(G, path)
    except Exception as e:
        return {"error": str(e)}

def format_route(G, path):
    distance = 0
    time = 0
    risks = []
    risk_probs = []

    for u, v in zip(path[:-1], path[1:]):
        edge = G[u][v]
        distance += edge["distance_km"]
        time += edge["travel_time_min"]
        risks.append(edge["risk"])
        risk_probs.append(edge.get("risk_probability", 0.0))

    risk_priority = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    risk_score = max(risks, key=lambda r: risk_priority[r])
    risk_reason = ", ".join(set(risks))
    risk_probability = round(sum(risk_probs) / len(risk_probs), 2) if risk_probs else 0.0

    return {
        "route": path,
        "distance_km": round(distance, 2),
        "travel_time_min": round(time, 2),
        "risk_score": risk_score,
        "risk_probability": risk_probability,
        "risk_reason": risk_reason
    }
