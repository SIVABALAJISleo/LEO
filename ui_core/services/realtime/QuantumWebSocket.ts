/**
 * src/services/realtime/QuantumWebSocket.ts
 * Real-Time Telemetry & Event Broadcaster
 */
export class QuantumWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(url: string = "ws://localhost:8005/ws/telemetry") {
    this.url = url;
  }

  public connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log("[LEO Quantum WS] Real-time connection established.");
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (e) {
          console.warn("[LEO Quantum WS] Unparseable payload received:", event.data);
        }
      };

      this.ws.onclose = () => {
        this.attemptReconnect();
      };

      this.ws.onerror = (err) => {
        console.warn("[LEO Quantum WS] Error:", err);
      };
    } catch (e) {
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(30000, Math.pow(2, this.reconnectAttempts) * 1000);
      setTimeout(() => {
        this.connect();
      }, delay);
    }
  }

  private handleMessage(data: any) {
    switch (data.type) {
      case "benchmark_update":
        window.dispatchEvent(new CustomEvent("leo:benchmark", { detail: data }));
        break;
      case "swarm_update":
        window.dispatchEvent(new CustomEvent("leo:swarm", { detail: data }));
        break;
      case "memory_update":
        window.dispatchEvent(new CustomEvent("leo:memory", { detail: data }));
        break;
      default:
        window.dispatchEvent(new CustomEvent("leo:telemetry", { detail: data }));
    }
  }

  public send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  public disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
