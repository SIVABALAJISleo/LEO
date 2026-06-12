// LEO AI V31 — Phase 4 Paged Memory System
// Inspired by vLLM & PagedAttention. Uses dynamic page table allocations to make GPU KV context memory elastic.

export interface MemoryBlock {
  blockId: number;
  allocatedTokens: number;
  maxTokens: number;
  isCompacted: boolean;
  assignedRequestId: string | null;
}

export interface PagedMemoryTelemetry {
  totalBlocks: number;
  allocatedBlocksCount: number;
  freeBlocksCount: number;
  cacheUtilizationPct: number;
  fragmentationPct: number;
  compactedCount: number;
  pageTable: Record<string, number[]>; // request ID -> block IDs
}

export class PagedMemoryEngine {
  private blockCapacity = 16; // 16 tokens per block
  private blocks: MemoryBlock[] = [];
  private pageTable: Record<string, number[]> = {};

  constructor(totalBlocksCount: number = 512) {
    for (let i = 0; i < totalBlocksCount; i++) {
      this.blocks.push({
        blockId: i,
        allocatedTokens: 0,
        maxTokens: this.blockCapacity,
        isCompacted: false,
        assignedRequestId: null
      });
    }
  }

  allocate(requestId: string, tokenCount: number): number[] {
    const blocksNeeded = Math.ceil(tokenCount / this.blockCapacity);
    const allocatedBlocks: number[] = [];
    
    // Find free blocks
    let allocated = 0;
    for (const b of this.blocks) {
      if (b.assignedRequestId === null) {
        b.assignedRequestId = requestId;
        
        const remainingTokens = tokenCount - allocated;
        b.allocatedTokens = Math.min(this.blockCapacity, remainingTokens);
        allocated += b.allocatedTokens;
        
        allocatedBlocks.push(b.blockId);
        if (allocated >= tokenCount) break;
      }
    }
    
    this.pageTable[requestId] = allocatedBlocks;
    return allocatedBlocks;
  }

  release(requestId: string): void {
    const assignedBlocks = this.pageTable[requestId] || [];
    for (const blockId of assignedBlocks) {
      const b = this.blocks[blockId];
      if (b) {
        b.assignedRequestId = null;
        b.allocatedTokens = 0;
        b.isCompacted = false;
      }
    }
    delete this.pageTable[requestId];
  }

  compactMemory(): number {
    // Merge partially filled blocks with the same request ID or move empty slots
    let compactedCount = 0;
    
    // Simple simulation of compaction: count blocks that are sparse (< 50% utilization) and flag as compacted
    for (const b of this.blocks) {
      if (b.assignedRequestId !== null && b.allocatedTokens < this.blockCapacity / 2 && !b.isCompacted) {
        b.isCompacted = true;
        compactedCount++;
      }
    }
    return compactedCount;
  }

  getTelemetry(): PagedMemoryTelemetry {
    const allocatedBlocksCount = this.blocks.filter(b => b.assignedRequestId !== null).length;
    const freeBlocksCount = this.blocks.length - allocatedBlocksCount;
    const totalAllocatedTokens = this.blocks.reduce((acc, b) => acc + b.allocatedTokens, 0);
    const capacityTokens = allocatedBlocksCount * this.blockCapacity;
    
    const cacheUtilizationPct = parseFloat(((allocatedBlocksCount / this.blocks.length) * 100).toFixed(1));
    const fragmentationPct = capacityTokens > 0 
      ? parseFloat(((1.0 - (totalAllocatedTokens / capacityTokens)) * 100).toFixed(1)) 
      : 0;

    const compactedCount = this.blocks.filter(b => b.isCompacted).length;

    return {
      totalBlocks: this.blocks.length,
      allocatedBlocksCount,
      freeBlocksCount,
      cacheUtilizationPct,
      fragmentationPct,
      compactedCount,
      pageTable: { ...this.pageTable }
    };
  }
}
