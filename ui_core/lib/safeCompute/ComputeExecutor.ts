import { v4 as uuidv4 } from 'uuid';

// ComputeExecutor - Abstract compute execution layer
// Multi-machine ready: prepares system for additional compute nodes

export type ExecutorType = 'local' | 'remote' | 'distributed';

export interface ComputeNode {
  id: string;
  type: ExecutorType;
  status: 'online' | 'offline' | 'busy';
  capabilities: NodeCapabilities;
  lastHeartbeat: Date;
}

export interface NodeCapabilities {
  gpuAvailable: boolean;
  gpuMemoryMb: number;
  cpuCores: number;
  maxConcurrentJobs: number;
}

export interface ExecutionRequest {
  jobId: string;
  jobType: string;
  payload: unknown;
  priority: number;
  deadline?: Date;
}

export interface ExecutionResult {
  jobId: string;
  nodeId: string;
  success: boolean;
  data?: unknown;
  error?: string;
  executionTimeMs: number;
}

type ExecutionListener = (result: ExecutionResult) => void;

class ComputeExecutor {
  private nodes: Map<string, ComputeNode> = new Map();
  private pendingJobs: Map<string, ExecutionRequest> = new Map();
  private listeners: Set<ExecutionListener> = new Set();
  private localNodeId: string;

  constructor() {
    // Initialize local node
    this.localNodeId = 'local-' + uuidv4().slice(0, 8);
    this.registerLocalNode();
  }

  // Register the local machine as a compute node
  private registerLocalNode(): void {
    const localNode: ComputeNode = {
      id: this.localNodeId,
      type: 'local',
      status: 'online',
      capabilities: {
        gpuAvailable: true, // Will be detected
        gpuMemoryMb: 8192, // Default, will be updated
        cpuCores: navigator.hardwareConcurrency || 4,
        maxConcurrentJobs: 1,
      },
      lastHeartbeat: new Date(),
    };
    this.nodes.set(this.localNodeId, localNode);
  }

  // Submit job for execution
  async execute(request: ExecutionRequest): Promise<ExecutionResult> {
    const startTime = Date.now();

    // Select best available node
    const node = this.selectNode(request);

    if (!node) {
      return {
        jobId: request.jobId,
        nodeId: 'none',
        success: false,
        error: 'No available compute nodes',
        executionTimeMs: 0,
      };
    }

    // Mark node as busy
    node.status = 'busy';
    this.pendingJobs.set(request.jobId, request);

    try {
      // Execute on selected node (currently only local)
      const data = await this.executeOnNode(node, request);

      const result: ExecutionResult = {
        jobId: request.jobId,
        nodeId: node.id,
        success: true,
        data,
        executionTimeMs: Date.now() - startTime,
      };

      node.status = 'online';
      this.pendingJobs.delete(request.jobId);
      this.notifyListeners(result);

      return result;
    } catch (error) {
      node.status = 'online';
      this.pendingJobs.delete(request.jobId);

      const result: ExecutionResult = {
        jobId: request.jobId,
        nodeId: node.id,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        executionTimeMs: Date.now() - startTime,
      };

      this.notifyListeners(result);
      return result;
    }
  }

  // Get all registered nodes
  getNodes(): ComputeNode[] {
    return Array.from(this.nodes.values());
  }

  // Get local node
  getLocalNode(): ComputeNode | null {
    return this.nodes.get(this.localNodeId) ?? null;
  }

  // Check if multi-node is possible
  isMultiNodeReady(): boolean {
    return this.nodes.size > 1;
  }

  // Register remote node (future use)
  registerNode(node: Omit<ComputeNode, 'lastHeartbeat'>): void {
    this.nodes.set(node.id, {
      ...node,
      lastHeartbeat: new Date(),
    });
  }

  // Update node heartbeat
  heartbeat(nodeId: string): void {
    const node = this.nodes.get(nodeId);
    if (node) {
      node.lastHeartbeat = new Date();
    }
  }

  // Remove offline nodes
  pruneOfflineNodes(maxAgeMs: number = 60000): void {
    const cutoff = Date.now() - maxAgeMs;
    for (const [id, node] of this.nodes) {
      if (id !== this.localNodeId && node.lastHeartbeat.getTime() < cutoff) {
        this.nodes.delete(id);
      }
    }
  }

  // Get pending jobs
  getPendingJobs(): ExecutionRequest[] {
    return Array.from(this.pendingJobs.values());
  }

  // Subscribe to execution results
  subscribe(listener: ExecutionListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // Update local node capabilities
  updateLocalCapabilities(capabilities: Partial<NodeCapabilities>): void {
    const local = this.nodes.get(this.localNodeId);
    if (local) {
      local.capabilities = { ...local.capabilities, ...capabilities };
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  private selectNode(request: ExecutionRequest): ComputeNode | null {
    // For now, always use local node
    // Future: implement load balancing across multiple nodes
    const availableNodes = Array.from(this.nodes.values())
      .filter(n => n.status === 'online');

    if (availableNodes.length === 0) return null;

    // Priority: local first, then by capability
    return availableNodes.find(n => n.type === 'local') || availableNodes[0];
  }

  private async executeOnNode(
    node: ComputeNode,
    request: ExecutionRequest
  ): Promise<unknown> {
    // Simulate execution based on job type
    const executionTime = this.estimateExecutionTime(request);
    await new Promise(resolve => setTimeout(resolve, Math.min(executionTime, 5000)));

    return {
      processed: true,
      nodeId: node.id,
      jobType: request.jobType,
      timestamp: new Date().toISOString(),
    };
  }

  private estimateExecutionTime(request: ExecutionRequest): number {
    // Estimate based on job type
    const baseTime: Record<string, number> = {
      'inference': 2000,
      'image_generation': 5000,
      'video_processing': 10000,
      'training': 30000,
      'analysis': 1500,
    };
    return baseTime[request.jobType] || 3000;
  }

  private notifyListeners(result: ExecutionResult): void {
    this.listeners.forEach(l => l(result));
  }
}

export const computeExecutor = new ComputeExecutor();
