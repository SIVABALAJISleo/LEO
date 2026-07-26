import { LazyExecutor } from "../optimization/LazyExecutor";

export interface MicroTask {
  id: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  run: () => Promise<any>;
}

export class TaskDecomposer {
  private static instance: TaskDecomposer;
  private lazy: LazyExecutor;

  private constructor() {
    this.lazy = LazyExecutor.getInstance();
  }

  static getInstance(): TaskDecomposer {
    if (!TaskDecomposer.instance) {
      TaskDecomposer.instance = new TaskDecomposer();
    }
    return TaskDecomposer.instance;
  }

  // Break a large array processing task into chunks
  async processInChunks<T, R>(
    items: T[],
    processor: (item: T) => Promise<R>,
    chunkSize: number = 10,
  ): Promise<R[]> {
    const results: R[] = [];
    const chunks = [];

    for (let i = 0; i < items.length; i += chunkSize) {
      chunks.push(items.slice(i, i + chunkSize));
    }

    // Execute chunks sequentially but yield to event loop via LazyExecutor logic (conceptually)
    // Here we just await them one by one to avoid UI freeze
    for (const chunk of chunks) {
      // Defer each chunk execution
      await this.lazy.defer(async () => {
        const chunkResults = await Promise.all(chunk.map(processor));
        results.push(...chunkResults);
      }, 1);
    }

    return results;
  }
}
