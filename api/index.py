from http.server import BaseHTTPRequestHandler
import json

DATA = [
  {"region": "apac", "service": "recommendations", "latency_ms": 164.26, "uptime_pct": 98.463},
  {"region": "apac", "service": "recommendations", "latency_ms": 161.1, "uptime_pct": 97.445},
  {"region": "apac", "service": "catalog", "latency_ms": 200.93, "uptime_pct": 98.956},
  {"region": "apac", "service": "checkout", "latency_ms": 169.96, "uptime_pct": 97.423},
  {"region": "apac", "service": "recommendations", "latency_ms": 127.3, "uptime_pct": 97.826},
  {"region": "apac", "service": "catalog", "latency_ms": 234.17, "uptime_pct": 98.305},
  {"region": "apac", "service": "recommendations", "latency_ms": 224.38, "uptime_pct": 97.66},
  {"region": "apac", "service": "analytics", "latency_ms": 220.9, "uptime_pct": 97.443},
  {"region": "apac", "service": "checkout", "latency_ms": 174.83, "uptime_pct": 97.379},
  {"region": "apac", "service": "catalog", "latency_ms": 103.73, "uptime_pct": 97.801},
  {"region": "apac", "service": "support", "latency_ms": 134.63, "uptime_pct": 98.369},
  {"region": "apac", "service": "payments", "latency_ms": 120.13, "uptime_pct": 98.39},
  {"region": "emea", "service": "analytics", "latency_ms": 136.28, "uptime_pct": 99.361},
  {"region": "emea", "service": "support", "latency_ms": 221.03, "uptime_pct": 98.021},
  {"region": "emea", "service": "support", "latency_ms": 117.64, "uptime_pct": 99.451},
  {"region": "emea", "service": "payments", "latency_ms": 213.75, "uptime_pct": 98.06},
  {"region": "emea", "service": "catalog", "latency_ms": 117.93, "uptime_pct": 99.234},
  {"region": "emea", "service": "recommendations", "latency_ms": 136.89, "uptime_pct": 97.253},
  {"region": "emea", "service": "support", "latency_ms": 145.82, "uptime_pct": 98.717},
  {"region": "emea", "service": "checkout", "latency_ms": 107.58, "uptime_pct": 98.934},
  {"region": "emea", "service": "analytics", "latency_ms": 169.04, "uptime_pct": 99.359},
  {"region": "emea", "service": "analytics", "latency_ms": 121.66, "uptime_pct": 98.303},
  {"region": "emea", "service": "recommendations", "latency_ms": 183.97, "uptime_pct": 99.16},
  {"region": "emea", "service": "payments", "latency_ms": 114.84, "uptime_pct": 98.829},
  {"region": "amer", "service": "analytics", "latency_ms": 192.13, "uptime_pct": 97.438},
  {"region": "amer", "service": "recommendations", "latency_ms": 169.13, "uptime_pct": 98.642},
  {"region": "amer", "service": "recommendations", "latency_ms": 106.12, "uptime_pct": 97.704},
  {"region": "amer", "service": "support", "latency_ms": 135.92, "uptime_pct": 97.132},
  {"region": "amer", "service": "analytics", "latency_ms": 143.35, "uptime_pct": 97.496},
  {"region": "amer", "service": "checkout", "latency_ms": 132.56, "uptime_pct": 97.662},
  {"region": "amer", "service": "analytics", "latency_ms": 155.51, "uptime_pct": 98.277},
  {"region": "amer", "service": "checkout", "latency_ms": 142.17, "uptime_pct": 97.984},
  {"region": "amer", "service": "catalog", "latency_ms": 192.67, "uptime_pct": 98.653},
  {"region": "amer", "service": "analytics", "latency_ms": 157.46, "uptime_pct": 97.289},
  {"region": "amer", "service": "catalog", "latency_ms": 178.61, "uptime_pct": 97.14},
  {"region": "amer", "service": "analytics", "latency_ms": 140.55, "uptime_pct": 97.64}
]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
}

class handler(BaseHTTPRequestHandler):

    def send_cors_headers(self):
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        req = json.loads(body)

        regions = req.get("regions", [])
        threshold_ms = req.get("threshold_ms", 0)

        result = {}
        for region in regions:
            records = [r for r in DATA if r["region"] == region]
            if not records:
                result[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
                continue
            latencies = sorted([r["latency_ms"] for r in records])
            uptimes = [r["uptime_pct"] for r in records]
            n = len(latencies)
            idx = max(int(round(0.95 * n)) - 1, 0)
            result[region] = {
                "avg_latency": round(sum(latencies) / n, 4),
                "p95_latency": round(latencies[idx], 4),
                "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
                "breaches": sum(1 for l in latencies if l > threshold_ms)
            }

        response = json.dumps(result).encode()
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(response)
