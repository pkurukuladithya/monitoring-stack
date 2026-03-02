import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

PROM_URL = "http://hs-prometheus:9090"

app = FastAPI()

def query(promql: str) -> float:
    r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": promql}, timeout=5)
    r.raise_for_status()
    data = r.json()
    result = data["data"]["result"]
    if not result:
        return float("nan")
    return float(result[0]["value"][1])

@app.get("/", response_class=HTMLResponse)
def home():
    # CPU % (approx)
    cpu = query('100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])))')

    # RAM used %
    mem_used = query('100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))')

    # Disk used % (root filesystem)
    disk_used = query('100 * (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}))')

    # Running containers count (from cAdvisor)
    containers = query('count(container_last_seen{container_label_com_docker_compose_project!=""})')

    html = f"""
    <html>
    <head>
      <title>HS Control Center</title>
      <style>
        body {{ font-family: Arial; background:#0b1220; color:#e5e7eb; padding:24px; }}
        .card {{ background:#111827; border:1px solid #1f2937; border-radius:16px; padding:18px; margin:12px 0; }}
        .big {{ font-size:38px; font-weight:700; }}
        .label {{ color:#9ca3af; }}
      </style>
    </head>
    <body>
      <h1>HS Control Center</h1>

      <div class="card">
        <div class="label">CPU Usage</div>
        <div class="big">{cpu:.1f}%</div>
      </div>

      <div class="card">
        <div class="label">Memory Used</div>
        <div class="big">{mem_used:.1f}%</div>
      </div>

      <div class="card">
        <div class="label">Disk Used (/)</div>
        <div class="big">{disk_used:.1f}%</div>
      </div>

      <div class="card">
        <div class="label">Running Containers (approx)</div>
        <div class="big">{containers:.0f}</div>
      </div>

      <p class="label">Data source: Prometheus</p>
    </body>
    </html>
    """
    return html