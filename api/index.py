from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json, os, statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load data from JSON file
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data.json")
with open(DATA_PATH) as f:
    DATA = json.load(f)

class Request(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/api")
def analytics(req: Request):
    result = {}
    for region in req.regions:
        records = [r for r in DATA if r["region"] == region]
        if not records:
            result[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
            continue
        latencies = sorted([r["latency_ms"] for r in records])
        uptimes = [r["uptime_pct"] for r in records]
        n = len(latencies)
        # p95 using nearest rank
        idx = max(int(round(0.95 * n)) - 1, 0)
        p95 = latencies[idx]
        result[region] = {
            "avg_latency": round(sum(latencies) / n, 4),
            "p95_latency": round(p95, 4),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
            "breaches": sum(1 for l in latencies if l > req.threshold_ms)
        }
    return result
