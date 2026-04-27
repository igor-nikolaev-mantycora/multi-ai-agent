import React, { useState } from "react";

export default function App() {
  const [q, setQ] = useState("");
  const [data, setData] = useState(null);

  const run = async () => {
    const r = await fetch(`http://127.0.0.1:8000/ask?q=${encodeURIComponent(q)}`);
    setData(await r.json());
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Multi-AI System</h2>

      <input value={q} onChange={e=>setQ(e.target.value)} style={{width:"70%"}} />
      <button onClick={run}>Run</button>

      {data && (
        <>
          <h3>Consensus</h3>
          <pre>{data.consensus}</pre>

          <h3>Contradictions</h3>
          <pre>{data.contradictions}</pre>

          <h3>Scores</h3>
          <pre>{data.scores}</pre>

          <h3>Costs</h3>
          <pre>{JSON.stringify(data.costs,null,2)}</pre>

          <h3>Answers</h3>
          {Object.entries(data.answers).map(([k,v])=>(
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