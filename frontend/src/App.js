import React, { useState } from "react";

export default function App() {
  const [q, setQ] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const renderValue = (value) => {
    if (value == null) {
      return "";
    }

    if (typeof value === "string") {
      return value;
    }

    return JSON.stringify(value, null, 2);
  };

  const run = async () => {
    setLoading(true);
    setError("");

    try {
      const r = await fetch(`http://127.0.0.1:8000/ask?q=${encodeURIComponent(q)}`);
      const payload = await r.json();

      if (!r.ok) {
        throw new Error(payload.detail || "Request failed");
      }

      setData(payload);
    } catch (err) {
      setData(null);
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Multi-AI System (Free Tier)</h2>
      <p>Providers: Gemini API free tier, Hugging Face free credits, and local Ollama.</p>

      <input value={q} onChange={e=>setQ(e.target.value)} style={{width:"70%"}} />
      <button onClick={run} disabled={loading || !q.trim()}>
        {loading ? "Running..." : "Run"}
      </button>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {data && (
        <>
          <h3>Consensus</h3>
          <pre>{renderValue(data.consensus)}</pre>

          <h3>Contradictions</h3>
          <pre>{renderValue(data.contradictions)}</pre>

          <h3>Scores</h3>
          <pre>{renderValue(data.scores)}</pre>

          <h3>Costs</h3>
          <pre>{JSON.stringify(data.costs,null,2)}</pre>

          {data.errors && Object.keys(data.errors).length > 0 && (
            <>
              <h3>Provider Errors</h3>
              <pre>{JSON.stringify(data.errors, null, 2)}</pre>
            </>
          )}

          {data.providers && (
            <>
              <h3>Provider Status</h3>
              <pre>{JSON.stringify(data.providers, null, 2)}</pre>
            </>
          )}

          <h3>Answers</h3>
          {Object.entries(data.answers || {}).map(([k,v])=>(
            <div key={k}>
              <b>{k}</b>
              <p>{v}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
