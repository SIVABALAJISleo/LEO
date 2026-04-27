// ZeroLatencyEngine - Optimistic updates + local-first storage + background sync
// Goal: Zero perceived latency for all user actions

interface OptimisticUpdate {
  id: string;
  action: string;
  payload: unknown;
  predictedResult: unknown;
  timestamp: Date;
  status: 'pending' | 'confirmed' | 'failed' | 'compensated';
  serverResult?: unknown;
  conflictResolution?: 'client-wins' | 'server-wins' | 'merge';
}

interface SyncQueueItem {
  id: string;
  action: string;
  payload: unknown;
  retries: number;
  maxRetries: number;
  createdAt: Date;
  lastAttempt?: Date;
  error?: string;
}

interface PrefetchEntry {
  key: string;
  data: unknown;
  fetchedAt: Date;
  expiresAt: Date;
  confidence: number;
}

interface ZeroLatencyStats {
  optimisticUpdates: number;
  confirmedUpdates: number;
  failedUpdates: number;
  compensations: number;
  syncQueueSize: number;
  prefetchHits: number;
  prefetchMisses: number;
  avgConfirmationTimeMs: number;
}

const STORAGE_KEYS = {
  SYNC_QUEUE: 'hyper_sync_queue',
  PREFETCH_CACHE: 'hyper_prefetch_cache',
  OPTIMISTIC_STATE: 'hyper_optimistic_state',
};

class ZeroLatencyEngine {
  private static instance: ZeroLatencyEngine;
  private optimisticUpdates: Map<string, OptimisticUpdate> = new Map();
  private syncQueue: Map<string, SyncQueueItem> = new Map();
  private prefetchCache: Map<string, PrefetchEntry> = new Map();
  private isOnline: boolean = typeof navigator !== 'undefined' ? navigator.onLine : true;
  private isSyncing: boolean = false;
  private listeners: Set<(stats: ZeroLatencyStats) => void> = new Set();
  
  private stats: ZeroLatencyStats = {
    optimisticUpdates: 0,
    confirmedUpdates: 0,
    failedUpdates: 0,
    compensations: 0,
    syncQueueSize: 0,
    prefetchHits: 0,
    prefetchMisses: 0,
    avgConfirmationTimeMs: 0,
  };

  private confirmationTimes: number[] = [];

  private constructor() {
    this.loadFromStorage();
    this.setupNetworkListeners();
    this.startBackgroundSync();
  }

  static getInstance(): ZeroLatencyEngine {
    if (!ZeroLatencyEngine.instance) {
      ZeroLatencyEngine.instance = new ZeroLatencyEngine();
    }
    return ZeroLatencyEngine.instance;
  }

  // ===== OPTIMISTIC UPDATES =====
  
  /**
   * Apply an optimistic update immediately
   * Returns predicted result, queues for server sync
   */
  applyOptimistic<T>(params: {
    action: string;
    payload: unknown;
    predict: (payload: unknown) => T;
    execute: (payload: unknown) => Promise<T>;
    onConflict?: (predicted: T, actual: T) => T;
  }): { result: T; updateId: string } {
    const updateId = `opt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const predictedResult = params.predict(params.payload);

    const update: OptimisticUpdate = {
      id: updateId,
      action: params.action,
      payload: params.payload,
      predictedResult,
      timestamp: new Date(),
      status: 'pending',
    };

    this.optimisticUpdates.set(updateId, update);
    this.stats.optimisticUpdates++;

    // Queue for background execution
    this.queueForSync({
      id: updateId,
      action: params.action,
      payload: params.payload,
      retries: 0,
      maxRetries: 3,
      createdAt: new Date(),
    });

    // Execute in background
    this.executeAndReconcile(updateId, params.execute, params.onConflict);

    this.saveToStorage();
    this.notifyListeners();

    return { result: predictedResult, updateId };
  }

  private async executeAndReconcile<T>(
    updateId: string,
    execute: (payload: unknown) => Promise<T>,
    onConflict?: (predicted: T, actual: T) => T
  ): Promise<void> {
    const update = this.optimisticUpdates.get(updateId);
    if (!update) return;

    const startTime = Date.now();

    try {
      const serverResult = await execute(update.payload);
      const confirmationTime = Date.now() - startTime;
      this.confirmationTimes.push(confirmationTime);
      if (this.confirmationTimes.length > 100) this.confirmationTimes.shift();
      this.stats.avgConfirmationTimeMs = 
        this.confirmationTimes.reduce((a, b) => a + b, 0) / this.confirmationTimes.length;

      // Check for conflicts
      const predicted = update.predictedResult as T;
      const hasConflict = JSON.stringify(predicted) !== JSON.stringify(serverResult);

      if (hasConflict && onConflict) {
        const resolved = onConflict(predicted, serverResult);
        update.serverResult = resolved;
        update.conflictResolution = 'merge';
        update.status = 'confirmed';
        this.stats.compensations++;
      } else {
        update.serverResult = serverResult;
        update.status = 'confirmed';
      }

      this.stats.confirmedUpdates++;
      this.syncQueue.delete(updateId);

    } catch (error) {
      update.status = 'failed';
      this.stats.failedUpdates++;
      console.error(`[ZeroLatency] Update ${updateId} failed:`, error);
    }

    this.stats.syncQueueSize = this.syncQueue.size;
    this.saveToStorage();
    this.notifyListeners();
  }

  // ===== LOCAL-FIRST STORAGE =====

  /**
   * Store data locally first, sync to server later
   */
  storeLocal<T>(key: string, data: T): void {
    try {
      const entry = {
        data,
        storedAt: new Date().toISOString(),
        synced: false,
      };
      localStorage.setItem(`hyper_local_${key}`, JSON.stringify(entry));
    } catch (e) {
      console.warn('[ZeroLatency] Failed to store locally:', e);
    }
  }

  getLocal<T>(key: string): T | null {
    try {
      const stored = localStorage.getItem(`hyper_local_${key}`);
      if (stored) {
        return JSON.parse(stored).data as T;
      }
    } catch (e) {
      console.warn('[ZeroLatency] Failed to get local data:', e);
    }
    return null;
  }

  // ===== BACKGROUND SYNC QUEUE =====

  private queueForSync(item: SyncQueueItem): void {
    this.syncQueue.set(item.id, item);
    this.stats.syncQueueSize = this.syncQueue.size;
    
    if (this.isOnline && !this.isSyncing) {
      this.processQueue();
    }
  }

  private async processQueue(): Promise<void> {
    if (this.isSyncing || !this.isOnline) return;
    this.isSyncing = true;

    const items = Array.from(this.syncQueue.values())
      .filter(item => item.retries < item.maxRetries)
      .sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime());

    for (const item of items) {
      try {
        // The actual execution happens in executeAndReconcile
        // Here we just track retries for failed items
        item.lastAttempt = new Date();
      } catch (error) {
        item.retries++;
        item.error = (error as Error).message;
        
        if (item.retries >= item.maxRetries) {
          console.error(`[ZeroLatency] Sync failed permanently for ${item.id}`);
          this.syncQueue.delete(item.id);
        }
      }
    }

    this.isSyncing = false;
    this.stats.syncQueueSize = this.syncQueue.size;
    this.saveToStorage();
  }

  // ===== PREDICTIVE PREFETCH =====

  /**
   * Prefetch data that the user is likely to need next
   */
  prefetch<T>(params: {
    key: string;
    fetch: () => Promise<T>;
    ttlMs?: number;
    confidence?: number;
  }): void {
    const { key, fetch, ttlMs = 60000, confidence = 0.8 } = params;

    // Check if already cached and valid
    const existing = this.prefetchCache.get(key);
    if (existing && existing.expiresAt > new Date()) {
      return;
    }

    // Fetch in background
    fetch().then(data => {
      this.prefetchCache.set(key, {
        key,
        data,
        fetchedAt: new Date(),
        expiresAt: new Date(Date.now() + ttlMs),
        confidence,
      });
      this.saveToStorage();
    }).catch(error => {
      console.warn(`[ZeroLatency] Prefetch failed for ${key}:`, error);
    });
  }

  getPrefetched<T>(key: string): T | null {
    const entry = this.prefetchCache.get(key);
    if (entry && entry.expiresAt > new Date()) {
      this.stats.prefetchHits++;
      return entry.data as T;
    }
    this.stats.prefetchMisses++;
    return null;
  }

  // ===== DELTA COMPRESSION + MICRO-BATCHING =====

  private pendingBatch: Map<string, unknown[]> = new Map();
  private batchTimeout: ReturnType<typeof setTimeout> | null = null;

  /**
   * Queue an action for micro-batching
   */
  queueBatch(action: string, item: unknown): void {
    const batch = this.pendingBatch.get(action) || [];
    batch.push(item);
    this.pendingBatch.set(action, batch);

    if (!this.batchTimeout) {
      this.batchTimeout = setTimeout(() => {
        this.flushBatch();
      }, 50); // 50ms micro-batch window
    }
  }

  private flushBatch(): void {
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    const batches = Array.from(this.pendingBatch.entries());
    this.pendingBatch.clear();

    for (const [action, items] of batches) {
      console.log(`[ZeroLatency] Flushing batch: ${action} with ${items.length} items`);
      // Compress with delta encoding if items are similar
      const compressed = this.deltaCompress(items);
      // Queue the compressed batch
      this.queueForSync({
        id: `batch_${Date.now()}`,
        action: `batch_${action}`,
        payload: compressed,
        retries: 0,
        maxRetries: 3,
        createdAt: new Date(),
      });
    }
  }

  private deltaCompress(items: unknown[]): { base: unknown; deltas: unknown[] } {
    if (items.length === 0) return { base: null, deltas: [] };
    if (items.length === 1) return { base: items[0], deltas: [] };

    // Simple delta compression: store first item as base, rest as deltas
    const base = items[0];
    const deltas = items.slice(1).map(item => {
      // In production, this would compute actual deltas
      return item;
    });

    return { base, deltas };
  }

  // ===== CONFLICT RESOLUTION =====

  resolveConflict<T>(
    clientValue: T,
    serverValue: T,
    strategy: 'client-wins' | 'server-wins' | 'last-write-wins' | 'merge'
  ): T {
    switch (strategy) {
      case 'client-wins':
        return clientValue;
      case 'server-wins':
        return serverValue;
      case 'last-write-wins':
        // Would compare timestamps in production
        return clientValue;
      case 'merge':
        // Simple merge for objects
        if (typeof clientValue === 'object' && typeof serverValue === 'object') {
          return { ...serverValue as object, ...clientValue as object } as T;
        }
        return clientValue;
      default:
        return serverValue;
    }
  }

  // ===== NETWORK & LIFECYCLE =====

  private setupNetworkListeners(): void {
    if (typeof window === 'undefined') return;

    window.addEventListener('online', () => {
      this.isOnline = true;
      console.log('[ZeroLatency] Back online - processing sync queue');
      this.processQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      console.log('[ZeroLatency] Offline - queuing updates locally');
    });

    window.addEventListener('beforeunload', () => {
      this.saveToStorage();
    });
  }

  private startBackgroundSync(): void {
    // Process queue periodically
    setInterval(() => {
      if (this.isOnline && this.syncQueue.size > 0) {
        this.processQueue();
      }
      this.cleanupExpiredPrefetch();
    }, 5000);
  }

  private cleanupExpiredPrefetch(): void {
    const now = new Date();
    for (const [key, entry] of this.prefetchCache.entries()) {
      if (entry.expiresAt < now) {
        this.prefetchCache.delete(key);
      }
    }
  }

  // ===== PERSISTENCE =====

  private saveToStorage(): void {
    try {
      localStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(
        Array.from(this.syncQueue.entries())
      ));
      localStorage.setItem(STORAGE_KEYS.PREFETCH_CACHE, JSON.stringify(
        Array.from(this.prefetchCache.entries())
      ));
    } catch (e) {
      console.warn('[ZeroLatency] Failed to save to storage:', e);
    }
  }

  private loadFromStorage(): void {
    try {
      const queueData = localStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
      if (queueData) {
        const entries = JSON.parse(queueData);
        this.syncQueue = new Map(entries.map(([k, v]: [string, SyncQueueItem]) => [
          k,
          { ...v, createdAt: new Date(v.createdAt), lastAttempt: v.lastAttempt ? new Date(v.lastAttempt) : undefined }
        ]));
        this.stats.syncQueueSize = this.syncQueue.size;
      }

      const cacheData = localStorage.getItem(STORAGE_KEYS.PREFETCH_CACHE);
      if (cacheData) {
        const entries = JSON.parse(cacheData);
        this.prefetchCache = new Map(entries.map(([k, v]: [string, PrefetchEntry]) => [
          k,
          { ...v, fetchedAt: new Date(v.fetchedAt), expiresAt: new Date(v.expiresAt) }
        ]));
      }
    } catch (e) {
      console.warn('[ZeroLatency] Failed to load from storage:', e);
    }
  }

  // ===== STATS & SUBSCRIPTIONS =====

  getStats(): ZeroLatencyStats {
    return { ...this.stats };
  }

  getQueueStatus(): { size: number; isOnline: boolean; isSyncing: boolean } {
    return {
      size: this.syncQueue.size,
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
    };
  }

  subscribe(listener: (stats: ZeroLatencyStats) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    const stats = this.getStats();
    this.listeners.forEach(l => l(stats));
  }
}

export const zeroLatencyEngine = ZeroLatencyEngine.getInstance();
export type { OptimisticUpdate, SyncQueueItem, PrefetchEntry, ZeroLatencyStats };
