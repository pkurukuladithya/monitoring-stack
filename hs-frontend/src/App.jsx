import { useEffect, useState } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [summary, setSummary] = useState(null);
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    const s = await fetch(`${API}/api/metrics/summary`).then(r => r.json());
    const c = await fetch(`${API}/api/containers`).then(r => r.json());
    setSummary(s);
    setContainers(c);
    setLoading(false);
  }

  async function action(name, act) {
    await fetch(`${API}/api/containers/${name}/${act}`, { method: "POST" });
    refresh();
  }

  useEffect(() => { refresh(); }, []);

  if (loading) return <div style={{padding: 20}}>Loading...</div>;

  const status =
    summary.down_targets > 0 ? "CRITICAL" :
    (summary.cpu_pct > 90 || summary.mem_pct > 90 || summary.disk_pct > 90) ? "WARNING" :
    "HEALTHY";

  return (
    <div style={{fontFamily:"Arial", padding:20}}>
      <h1>HS Control Center</h1>

      <div style={{marginBottom:12, fontSize:18}}>
        Status: <b>{status}</b>
      </div>

      <div style={{display:"grid", gridTemplateColumns:"repeat(4, 1fr)", gap:12}}>
        <Card title="CPU">{summary.cpu_pct?.toFixed(1)}%</Card>
        <Card title="Memory">{summary.mem_pct?.toFixed(1)}%</Card>
        <Card title="Disk /">{summary.disk_pct?.toFixed(1)}%</Card>
        <Card title="Targets Down">{summary.down_targets}</Card>
      </div>

      <h2 style={{marginTop:20}}>Containers</h2>
      <table width="100%" cellPadding="8" style={{borderCollapse:"collapse"}}>
        <thead>
          <tr style={{textAlign:"left"}}>
            <th>Name</th><th>Status</th><th>Image</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {containers.map(c => (
            <tr key={c.id} style={{borderTop:"1px solid #ddd"}}>
              <td>{c.name}</td>
              <td>{c.status}</td>
              <td style={{fontSize:12, color:"#555"}}>{c.image}</td>
              <td>
                <button onClick={() => action(c.name, "restart")}>Restart</button>{" "}
                <button onClick={() => action(c.name, "stop")}>Stop</button>{" "}
                <button onClick={() => action(c.name, "start")}>Start</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <button style={{marginTop:16}} onClick={refresh}>Refresh</button>
    </div>
  );
}

function Card({title, children}) {
  return (
    <div style={{border:"1px solid #ddd", borderRadius:12, padding:12}}>
      <div style={{fontSize:12, color:"#666"}}>{title}</div>
      <div style={{fontSize:24, fontWeight:700}}>{children}</div>
    </div>
  );
}