export interface MemoryBlock {
  id: string;
  category: "semantic" | "episodic" | "project" | "user" | "scientific";
  content: string;
  importance: number;
  timestamp: number;
}
export interface CacheLookupResult {
  hit: boolean;
  value: string;
  sourceType: "prompt" | "embedding" | "response" | "reasoning";
  similarityScore: number;
}
export class AdvancedMemorySystem {
  public async queryCache(prompt: string): Promise<CacheLookupResult> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/memory/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    return res.json();
  }
  public async addMemory(category: string, content: string, importance: number): Promise<void> {
    await fetch("http://localhost:8000/api/v1/v40/engines/memory/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, content, importance }),
    });
  }
  public async getMemories(): Promise<MemoryBlock[]> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/memory/all");
    return res.json();
  }
}
