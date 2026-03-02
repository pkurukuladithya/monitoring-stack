import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import docker

PROM_URL = os.getenv("PROM_URL", "http://hs-prometheus:9090")

app = FastAPI(title="HS Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later we can restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

docker_client = docker.from_env()

def prom_query(q: str) -> float:
    r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": q}, timeout=5)
    r.raise_for_status()
    result = r.json()["data"]["result"]
    if not result:
        return float("nan")
    return float(result[0]["value"][1])

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/metrics/summary")
def metrics_summary():
    cpu = prom_query('100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[2m])))')
    mem = prom_query('100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))')
    disk = prom_query('100 * (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}))')
    down_targets = prom_query("count(up == 0)")
    return {
        "cpu_pct": cpu,
        "mem_pct": mem,
        "disk_pct": disk,
        "down_targets": int(down_targets) if down_targets == down_targets else None,  # NaN safe
    }

@app.get("/api/containers")
def list_containers():
    containers = docker_client.containers.list(all=True)
    return [
        {
            "id": c.short_id,
            "name": c.name,
            "status": c.status,
            "image": (c.image.tags[0] if c.image.tags else "none"),
        }
        for c in containers
    ]

@app.post("/api/containers/{name}/restart")
def restart_container(name: str):
    docker_client.containers.get(name).restart()
    return {"ok": True}

@app.post("/api/containers/{name}/stop")
def stop_container(name: str):
    docker_client.containers.get(name).stop()
    return {"ok": True}

@app.post("/api/containers/{name}/start")
def start_container(name: str):
    docker_client.containers.get(name).start()
    return {"ok": True}