import { createRoot } from "react-dom/client";
import { initializeEngine } from "./lib/engine-init";
import App from "./App.tsx";
import "./index.css";

// Start the production-grade SaaS engine (non-blocking)
try {
  initializeEngine();
} catch (e) {
  console.error("[Engine] Failed to initialize engine layer:", e);
}

const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(<App />);
} else {
  console.error("Root element not found!");
}
