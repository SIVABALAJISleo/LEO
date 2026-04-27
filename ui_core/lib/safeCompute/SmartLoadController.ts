// SmartLoadController - Manages system load and performance
// Limits job rate when laptop is busy
// Smooths performance to prevent overheating

import { SystemLoad, ComputeConfig } from './types';

class SmartLoadController {
  private config: ComputeConfig = {
    maxConcurrentJobs: 2,
    thermalThreshold: 85,
    memoryThreshold: 90,
    autoDowngradeEnabled: true,
    offlineMode: false,
  };

  private systemLoad: SystemLoad = {
    cpuUsage: 0,
    memoryUsage: 0,
    gpuMemoryUsage: 0,
    temperature: 45,
    isOverheating: false,
    availableRam: 8192,
  };

  private listeners: Set<(load: SystemLoad) => void> = new Set();

  getConfig(): ComputeConfig {
    return { ...this.config };
  }

  updateConfig(updates: Partial<ComputeConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  getSystemLoad(): SystemLoad {
    return { ...this.systemLoad };
  }

  updateSystemLoad(updates: Partial<SystemLoad>): void {
    this.systemLoad = {
      ...this.systemLoad,
      ...updates,
      isOverheating: (updates.temperature ?? this.systemLoad.temperature) > this.config.thermalThreshold,
    };
    this.notifyListeners();
  }

  canAcceptNewJob(): boolean {
    // Check if system can handle a new job
    if (this.systemLoad.isOverheating) return false;
    if (this.systemLoad.memoryUsage > this.config.memoryThreshold) return false;
    return true;
  }

  shouldDowngradeComplexity(): boolean {
    // Auto-downgrade if RAM is low
    return this.config.autoDowngradeEnabled && 
           this.systemLoad.availableRam < 2048;
  }

  getRecommendedJobLimit(): number {
    if (this.systemLoad.isOverheating) return 0;
    if (this.systemLoad.memoryUsage > 80) return 1;
    if (this.systemLoad.cpuUsage > 70) return 1;
    return this.config.maxConcurrentJobs;
  }

  getLoadStatus(): 'idle' | 'light' | 'moderate' | 'heavy' | 'critical' {
    const avgLoad = (this.systemLoad.cpuUsage + this.systemLoad.memoryUsage) / 2;
    if (this.systemLoad.isOverheating) return 'critical';
    if (avgLoad < 20) return 'idle';
    if (avgLoad < 50) return 'light';
    if (avgLoad < 75) return 'moderate';
    return 'heavy';
  }

  /**
   * PRODUCTION HONESTY: System metrics require a Local Agent
   * Browsers cannot access OS-level hardware metrics.
   * This method sets default "unknown" values when no agent is connected.
   * Real metrics come ONLY from authenticated Local Agent heartbeats.
   */
  setDefaultUnknownMetrics(): void {
    // Set to "unknown" state - not simulated, honestly unavailable
    this.updateSystemLoad({
      cpuUsage: 0,
      memoryUsage: 0,
      gpuMemoryUsage: 0,
      temperature: 0,
      availableRam: 0,
    });
  }

  /**
   * Update with REAL metrics from Local Agent
   * Only call this with verified agent data
   */
  updateFromAgent(agentMetrics: {
    cpuUsage: number;
    memoryUsage: number;
    gpuMemoryUsage: number;
    temperature: number;
    availableRam: number;
  }): void {
    this.updateSystemLoad(agentMetrics);
  }

  subscribe(listener: (load: SystemLoad) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.systemLoad));
  }
}

export const smartLoadController = new SmartLoadController();
