import React, { useState } from "react";

function App() {
  const [q, setQ] = useState("");
  const [data, setData] = useState(null);

  const ask = async () => {
    const res = await fetch(`http://127.0.0.1:8000/ask?q=${encodeURIComponent(q)}`);
    const json = await res.json();
    setData(json);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Multi-AI Agent</h2>

      <input
        style={{ width: "80%" }}
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />

      <button onClick={ask}>Run</button>

      {data && (
        <>
          <h3>Consensus</h3>
          <pre>{JSON.stringify(data.consensus, null, 2)}</pre>

          <h3>Contradictions</h3>
          <pre>{data.contradictions}</pre>

          <h3>Answers</h3>
          {Object.entries(data.answers).map(([k, v]) => (
            <div key={k}>
              <h4>{k}</h4>
              <p>{v}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default App;