import React, { useState } from "react";

interface Hit {
  id: string;
  text: string;
  score: number;
  metadata: Record<string, unknown>;
}

const API = "/api";

export default function SearchUI() {
  const [query, setQuery] = useState("");
  const [collection, setCollection] = useState("demo");
  const [mode, setMode] = useState<"semantic" | "hybrid">("semantic");
  const [results, setResults] = useState<Hit[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, collection, n_results: 8, mode }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResults(data.results);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSearch} style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about your documents…"
          style={{ flex: 1, minWidth: 200, padding: "8px 12px", border: "1px solid #d1d5db", borderRadius: 6, fontSize: 14 }}
        />
        <input
          value={collection}
          onChange={(e) => setCollection(e.target.value)}
          placeholder="Collection"
          style={{ width: 120, padding: "8px 12px", border: "1px solid #d1d5db", borderRadius: 6, fontSize: 14 }}
        />
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value as "semantic" | "hybrid")}
          style={{ padding: "8px 10px", border: "1px solid #d1d5db", borderRadius: 6, fontSize: 14 }}
        >
          <option value="semantic">Semantic</option>
          <option value="hybrid">Hybrid</option>
        </select>
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "8px 20px",
            background: "#111",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: 14,
            fontWeight: 500,
          }}
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <p style={{ color: "#dc2626", marginBottom: 12, fontSize: 14 }}>{error}</p>}

      {results.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {results.map((hit) => (
            <div
              key={hit.id}
              style={{
                background: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: 8,
                padding: "14px 16px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 12, color: "#6b7280", fontFamily: "monospace" }}>{hit.id}</span>
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 600,
                    color: hit.score > 0.7 ? "#16a34a" : hit.score > 0.4 ? "#d97706" : "#6b7280",
                  }}
                >
                  score {hit.score.toFixed(3)}
                </span>
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.6, color: "#374151" }}>{hit.text}</p>
              {hit.metadata?.source && (
                <p style={{ fontSize: 12, color: "#9ca3af", marginTop: 6 }}>
                  source: {String(hit.metadata.source)}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <p style={{ color: "#9ca3af", fontSize: 14 }}>No results. Is the collection ingested?</p>
      )}
    </div>
  );
}
