import React, { useState } from "react";
import SearchUI from "./SearchUI";
import ClusterViz from "./ClusterViz";

type Tab = "search" | "cluster";

export default function App() {
  const [tab, setTab] = useState<Tab>("search");

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "24px 16px" }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>vector-embeddings</h1>
      <p style={{ color: "#555", marginBottom: 20, fontSize: 14 }}>
        Semantic search and cluster explorer over your own documents.
      </p>

      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        {(["search", "cluster"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: "6px 16px",
              borderRadius: 6,
              border: "1px solid #d1d5db",
              background: tab === t ? "#111" : "#fff",
              color: tab === t ? "#fff" : "#111",
              cursor: "pointer",
              fontWeight: 500,
              fontSize: 14,
            }}
          >
            {t === "search" ? "Search" : "Cluster explorer"}
          </button>
        ))}
      </div>

      {tab === "search" ? <SearchUI /> : <ClusterViz />}
    </div>
  );
}
