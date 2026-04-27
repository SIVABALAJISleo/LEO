// ThermalGuardian - Manages thermal safety
// Tracks CPU/GPU temperature
// Auto-pauses or slows jobs if too hot
// Prevents shutdown or throttling

interface ThermalState {
  cpuTemp: number;
  gpuTemp: number;
  fanSpeed: number;
  throttlingActive: boolean;
  emergencyShutdownPending: boolean;
}

interface ThermalThresholds {
  warning: number;
  critical: number;
  emergency: number;
}

class ThermalGuardian {
  private state: ThermalState = {
    cpuTemp: 45,
    gpuTemp: 40,
    fanSpeed: 30,
    throttlingActive: false,
    emergencyShutdownPending: false,
  };

  private thresholds: ThermalThresholds = {
    warning: 70,
    critical: 85,
    emergency: 95,
  };

  private isActive: boolean = true;
  private listeners: Set<(state: ThermalState) => void> = new Set();
  private pausedJobs: Set<string> = new Set();

  getState(): ThermalState {
    return { ...this.state };
  }

  getThresholds(): ThermalThresholds {
    return { ...this.thresholds };
  }

  isGuardActive(): boolean {
    return this.isActive;
  }

  setActive(active: boolean): void {
    this.isActive = active;
    this.notifyListeners();
  }

  updateTemperatures(cpuTemp: number, gpuTemp: number): void {
    const maxTemp = Math.max(cpuTemp, gpuTemp);
    
    this.state = {
      cpuTemp,
      gpuTemp,
      fanSpeed: this.calculateFanSpeed(maxTemp),
      throttlingActive: maxTemp >= this.thresholds.warning,
      emergencyShutdownPending: maxTemp >= this.thresholds.emergency,
    };
    
    this.notifyListeners();
  }

  private calculateFanSpeed(maxTemp: number): number {
    if (maxTemp < 50) return 30;
    if (maxTemp < 70) return 50;
    if (maxTemp < 85) return 80;
    return 100;
  }

  getThermalLevel(): 'safe' | 'warning' | 'critical' | 'emergency' {
    const maxTemp = Math.max(this.state.cpuTemp, this.state.gpuTemp);
    
    if (maxTemp >= this.thresholds.emergency) return 'emergency';
    if (maxTemp >= this.thresholds.critical) return 'critical';
    if (maxTemp >= this.thresholds.warning) return 'warning';
    return 'safe';
  }

  shouldPauseJobs(): boolean {
    return this.isActive && this.getThermalLevel() !== 'safe';
  }

  shouldThrottleJobs(): boolean {
    const level = this.getThermalLevel();
    return this.isActive && (level === 'warning' || level === 'critical');
  }

  shouldEmergencyStop(): boolean {
    return this.isActive && this.getThermalLevel() === 'emergency';
  }

  // Mark job as paused due to thermal
  pauseJobForThermal(jobId: string): void {
    this.pausedJobs.add(jobId);
  }

  // Resume job after thermal recovery
  resumeJobAfterThermal(jobId: string): boolean {
    if (this.pausedJobs.has(jobId) && this.getThermalLevel() === 'safe') {
      this.pausedJobs.delete(jobId);
      return true;
    }
    return false;
  }

  getPausedJobCount(): number {
    return this.pausedJobs.size;
  }

  // Get recommended action based on thermal state
  getRecommendedAction(): {
    action: 'continue' | 'throttle' | 'pause' | 'stop';
    message: string;
  } {
    const level = this.getThermalLevel();
    
    switch (level) {
      case 'emergency':
        return {
          action: 'stop',
          message: 'Emergency thermal shutdown - all jobs stopped for safety',
        };
      case 'critical':
        return {
          action: 'pause',
          message: 'Critical temperature - jobs paused until cooldown',
        };
      case 'warning':
        return {
          action: 'throttle',
          message: 'Elevated temperature - job speed reduced',
        };
      default:
        return {
          action: 'continue',
          message: 'Temperature normal - full speed operation',
        };
    }
  }

  /**
   * PRODUCTION HONESTY: Temperature metrics require a Local Agent
   * Browsers cannot access CPU/GPU temperature sensors.
   * This method sets default "unknown" values when no agent is connected.
   * Real temperatures come ONLY from authenticated Local Agent heartbeats.
   */
  setDefaultUnknownTemperatures(): void {
    // Set to "unknown" state (0 = no data, not simulated)
    this.updateTemperatures(0, 0);
  }

  /**
   * Update with REAL temperatures from Local Agent
   * Only call this with verified agent data
   */
  updateFromAgent(cpuTemp: number, gpuTemp: number): void {
    this.updateTemperatures(cpuTemp, gpuTemp);
  }

  subscribe(listener: (state: ThermalState) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.state));
  }
}

export const thermalGuardian = new ThermalGuardian();
