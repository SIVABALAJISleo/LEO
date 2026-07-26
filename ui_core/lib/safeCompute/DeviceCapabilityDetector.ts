// DeviceCapabilityDetector - Client-Side Adaptive Compute
// Detect device capability (GPU, RAM, CPU)
// Route medium jobs accordingly

type DeviceCapabilityLevel = "high" | "medium" | "low" | "minimal";

interface DeviceCapabilities {
  level: DeviceCapabilityLevel;
  hasWebGPU: boolean;
  hasWebGL2: boolean;
  estimatedRamGb: number;
  cpuCores: number;
  isMobile: boolean;
  gpuVendor: string | null;
  gpuRenderer: string | null;
  networkType: string;
  supportsWasm: boolean;
  supportsSharedArrayBuffer: boolean;
  performanceScore: number;
}

interface ComputeRouting {
  canRunFull: boolean;
  canRunQuantized: boolean;
  canRunProgressive: boolean;
  recommendedMode: "full" | "quantized" | "progressive" | "server";
  maxModelSizeMb: number;
  estimatedSpeedFactor: number;
}

class DeviceCapabilityDetector {
  private cachedCapabilities: DeviceCapabilities | null = null;
  private listeners: Set<(caps: DeviceCapabilities) => void> = new Set();

  async detect(): Promise<DeviceCapabilities> {
    if (this.cachedCapabilities) {
      return this.cachedCapabilities;
    }

    const hasWebGPU = await this.checkWebGPU();
    const hasWebGL2 = this.checkWebGL2();
    const gpuInfo = this.getGPUInfo();
    const estimatedRamGb = this.estimateRAM();
    const cpuCores = navigator.hardwareConcurrency || 2;
    const isMobile = this.checkMobile();
    const networkType = this.getNetworkType();
    const supportsWasm = this.checkWasmSupport();
    const supportsSharedArrayBuffer = this.checkSharedArrayBuffer();

    const performanceScore = this.calculatePerformanceScore({
      hasWebGPU,
      hasWebGL2,
      estimatedRamGb,
      cpuCores,
      isMobile,
      supportsWasm,
    });

    const level = this.determineLevel(performanceScore);

    this.cachedCapabilities = {
      level,
      hasWebGPU,
      hasWebGL2,
      estimatedRamGb,
      cpuCores,
      isMobile,
      gpuVendor: gpuInfo.vendor,
      gpuRenderer: gpuInfo.renderer,
      networkType,
      supportsWasm,
      supportsSharedArrayBuffer,
      performanceScore,
    };

    this.notifyListeners();
    return this.cachedCapabilities;
  }

  private async checkWebGPU(): Promise<boolean> {
    if (!("gpu" in navigator)) return false;
    try {
      const gpu = (navigator as Navigator & { gpu?: { requestAdapter: () => Promise<unknown> } })
        .gpu;
      if (!gpu) return false;
      const adapter = await gpu.requestAdapter();
      return !!adapter;
    } catch {
      return false;
    }
  }

  private checkWebGL2(): boolean {
    try {
      const canvas = document.createElement("canvas");
      return !!canvas.getContext("webgl2");
    } catch {
      return false;
    }
  }

  private getGPUInfo(): { vendor: string | null; renderer: string | null } {
    try {
      const canvas = document.createElement("canvas");
      const gl = canvas.getContext("webgl") || canvas.getContext("webgl2");
      if (!gl) return { vendor: null, renderer: null };

      const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
      if (!debugInfo) return { vendor: null, renderer: null };

      return {
        vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
        renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL),
      };
    } catch {
      return { vendor: null, renderer: null };
    }
  }

  private estimateRAM(): number {
    // Use deviceMemory API if available
    if ("deviceMemory" in navigator) {
      return (navigator as Navigator & { deviceMemory?: number }).deviceMemory || 4;
    }
    // Fallback estimation based on platform
    const isMobile = this.checkMobile();
    return isMobile ? 4 : 8;
  }

  private checkMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent,
    );
  }

  private getNetworkType(): string {
    const connection = (navigator as Navigator & { connection?: { effectiveType?: string } })
      .connection;
    return connection?.effectiveType || "unknown";
  }

  private checkWasmSupport(): boolean {
    try {
      return typeof WebAssembly === "object" && typeof WebAssembly.instantiate === "function";
    } catch {
      return false;
    }
  }

  private checkSharedArrayBuffer(): boolean {
    try {
      return typeof SharedArrayBuffer !== "undefined";
    } catch {
      return false;
    }
  }

  private calculatePerformanceScore(params: {
    hasWebGPU: boolean;
    hasWebGL2: boolean;
    estimatedRamGb: number;
    cpuCores: number;
    isMobile: boolean;
    supportsWasm: boolean;
  }): number {
    let score = 0;

    // WebGPU is best
    if (params.hasWebGPU) score += 40;
    else if (params.hasWebGL2) score += 25;

    // RAM
    score += Math.min(20, params.estimatedRamGb * 2);

    // CPU cores
    score += Math.min(20, params.cpuCores * 2.5);

    // Mobile penalty
    if (params.isMobile) score *= 0.7;

    // WASM bonus
    if (params.supportsWasm) score += 10;

    return Math.min(100, Math.max(0, score));
  }

  private determineLevel(score: number): DeviceCapabilityLevel {
    if (score >= 70) return "high";
    if (score >= 45) return "medium";
    if (score >= 25) return "low";
    return "minimal";
  }

  getComputeRouting(): ComputeRouting {
    const caps = this.cachedCapabilities || {
      level: "low" as DeviceCapabilityLevel,
      hasWebGPU: false,
      hasWebGL2: false,
      estimatedRamGb: 4,
      performanceScore: 30,
    };

    const routing: ComputeRouting = {
      canRunFull: caps.level === "high" && caps.hasWebGPU,
      canRunQuantized: caps.level === "high" || caps.level === "medium",
      canRunProgressive: caps.level !== "minimal",
      recommendedMode: "server",
      maxModelSizeMb: 0,
      estimatedSpeedFactor: 1,
    };

    switch (caps.level) {
      case "high":
        routing.recommendedMode = caps.hasWebGPU ? "full" : "quantized";
        routing.maxModelSizeMb = caps.estimatedRamGb * 256; // Use ~25% of RAM
        routing.estimatedSpeedFactor = caps.hasWebGPU ? 0.9 : 0.5;
        break;
      case "medium":
        routing.recommendedMode = "quantized";
        routing.maxModelSizeMb = caps.estimatedRamGb * 128;
        routing.estimatedSpeedFactor = 0.3;
        break;
      case "low":
        routing.recommendedMode = "progressive";
        routing.maxModelSizeMb = caps.estimatedRamGb * 64;
        routing.estimatedSpeedFactor = 0.15;
        break;
      default:
        routing.recommendedMode = "server";
        routing.maxModelSizeMb = 0;
        routing.estimatedSpeedFactor = 0;
    }

    return routing;
  }

  getLevelLabel(): string {
    const caps = this.cachedCapabilities;
    if (!caps) return "Unknown";

    const labels: Record<DeviceCapabilityLevel, string> = {
      high: "High Performance",
      medium: "Standard",
      low: "Basic",
      minimal: "Limited",
    };

    return labels[caps.level];
  }

  getLevelColor(): string {
    const caps = this.cachedCapabilities;
    if (!caps) return "muted";

    const colors: Record<DeviceCapabilityLevel, string> = {
      high: "text-green-500",
      medium: "text-blue-500",
      low: "text-yellow-500",
      minimal: "text-orange-500",
    };

    return colors[caps.level];
  }

  subscribe(listener: (caps: DeviceCapabilities) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    if (this.cachedCapabilities) {
      this.listeners.forEach((l) => l(this.cachedCapabilities!));
    }
  }

  // Force re-detection
  refresh(): void {
    this.cachedCapabilities = null;
    this.detect();
  }
}

export const deviceCapabilityDetector = new DeviceCapabilityDetector();
export type { DeviceCapabilities, DeviceCapabilityLevel, ComputeRouting };
