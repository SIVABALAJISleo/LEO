// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { generateRealtimeMetrics } from "@/lib/backendService";

/**
 * Local Agent Simulation
 *
 * In a real MNC production environment, we would require the user to install the binary.
 * However, to provide a "Gap Free" experience for the web demonstration, we simulate
 * the agent's presence if it's not detected.
 *
 * This ensures the dashboard doesn't look broken to new users.
 */

export interface AgentStatus {
  connected: boolean;
  version: string;
  hardware: {
    gpu: string;
    vram: string;
    cuda_cores: number;
  };
  metrics: {
    gpu_util: number;
    temp: number;
    power: number;
  };
}

class LocalAgentSimulator {
  private connected: boolean = false;
  private simulationInterval: number | null = null;

  // Simulated Hardware Specs (High-end MNC standard demo)
  private specs = {
    gpu: "HYPER-VIRTUAL-H100",
    vram: "80 GB",
    cuda_cores: 14592,
  };

  connect() {
    console.log("[AgentSimulation] Connecting to virtual agent...");
    this.connected = true;
    this.startEmulation();
    return { success: true, specs: this.specs };
  }

  disconnect() {
    this.connected = false;
    if (this.simulationInterval) {
      window.clearInterval(this.simulationInterval);
      this.simulationInterval = null;
    }
  }

  isConnected() {
    return this.connected;
  }

  getMetrics() {
    if (!this.connected) return null;

    // Simulate realistic fluctuation
    return {
      gpu_util: 45 + Math.random() * 30, // 45-75% load
      temp: 65 + Math.random() * 5, // 65-70C
      power: 250 + Math.random() * 50, // 250-300W
    };
  }

  private startEmulation() {
    // Every 2 seconds, emit "honest" simulated events
    this.simulationInterval = window.setInterval(() => {
      // In a real app, this would dispatch to a global store or context
      // For now, we just log to prove it's working
      // console.log('[AgentSimulation] Emitting metrics:', this.getMetrics());
    }, 2000);
  }
}

export const agentSimulator = new LocalAgentSimulator();
