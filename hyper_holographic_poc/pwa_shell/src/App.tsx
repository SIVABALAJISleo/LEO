import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [intent, setIntent] = useState("");
  const [response, setResponse] = useState("");
  const [crdtState, setCrdtState] = useState("Syncing...");

  useEffect(() => {
    // Mock CRDT Initialization
    setTimeout(() => {
      setCrdtState("CRDT Actor Online: Perfect Consensus Reached");
    }, 1000);
  }, []);

  const handleManifest = async () => {
    setResponse("Materializing intent...");
    try {
      // Connects to local cognitive engine
      const res = await fetch("http://localhost:8080/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: intent, max_tokens: 128 }),
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (e) {
      setResponse("[FALLBACK] The Cognitive Engine is offline. Please start it on port 8080.");
    }
  };

  return (
    <div className="holographic-container">
      <header>
        <h1>Generative Holographic Execution</h1>
        <p className="status-crdt">P2P State: {crdtState}</p>
      </header>

      <main>
        <section className="intent-section">
          <h2>Manifest Intent</h2>
          <textarea
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="Describe the software behavior to materialize..."
            rows={5}
          />
          <button onClick={handleManifest}>Materialize via iGPU</button>
        </section>

        <section className="response-section">
          <h2>Execution Graph Output</h2>
          <div className="output-box">{response || "Awaiting intent..."}</div>
        </section>
      </main>
    </div>
  );
}

export default App;
