import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";

interface Point {
  id: string;
  x: number;
  y: number;
  text: string;
  cluster: number;
  metadata: Record<string, unknown>;
}

const API = "/api";
const COLORS = ["#6366f1","#f59e0b","#10b981","#ef4444","#8b5cf6","#06b6d4","#f97316"];

export default function ClusterViz() {
  const [collection, setCollection] = useState("demo");
  const [nClusters, setNClusters] = useState(3);
  const [points, setPoints] = useState<Point[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/cluster/umap?collection=${collection}&n_clusters=${nClusters}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setPoints(data.points);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  const clusters = [...new Set(points.map((p) => p.cluster))].sort();
  const traces = clusters.map((c) => {
    const pts = points.filter((p) => p.cluster === c);
    return {
      x: pts.map((p) => p.x),
      y: pts.map((p) => p.y),
      text: pts.map((p) => p.text),
      mode: "markers" as const,
      type: "scatter" as const,
      name: `Cluster ${c}`,
      marker: { color: COLORS[c % COLORS.length], size: 8, opacity: 0.8 },
    };
  });

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 16, alignItems: "center", flexWrap: "wrap" }}>
        <input
          value={collection}
          onChange={(e) => setCollection(e.target.value)}
          placeholder="Collection"
          style={{ width: 130, padding: "7px 10px", border: "1px solid #d1d5db", borderRadius: 6, fontSize: 14 }}
        />
        <label style={{ fontSize: 14, color: "#374151" }}>
          Clusters:&nbsp;
          <input
            type="number"
            min={2}
            max={20}
            value={nClusters}
            onChange={(e) => setNClusters(Number(e.target.value))}
            style={{ width: 60, padding: "6px 8px", border: "1px solid #d1d5db", borderRadius: 6, fontSize: 14 }}
          />
        </label>
        <button
          onClick={load}
          disabled={loading}
          style={{
            padding: "7px 18px",
            background: "#111",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: 14,
          }}
        >
          {loading ? "Loading…" : "Visualise"}
        </button>
      </div>

      {error && <p style={{ color: "#dc2626", fontSize: 14 }}>{error}</p>}

      {points.length > 0 && (
        <Plot
          data={traces}
          layout={{
            width: 800,
            height: 520,
            paper_bgcolor: "#fff",
            plot_bgcolor: "#f9fafb",
            margin: { t: 24, r: 16, b: 40, l: 40 },
            legend: { orientation: "h", y: -0.12 },
            hovermode: "closest",
          }}
          config={{ displayModeBar: false }}
        />
      )}

      {!loading && points.length === 0 && (
        <p style={{ color: "#9ca3af", fontSize: 14 }}>
          No data. Ingest some documents first, then click Visualise.
        </p>
      )}
    </div>
  );
}
