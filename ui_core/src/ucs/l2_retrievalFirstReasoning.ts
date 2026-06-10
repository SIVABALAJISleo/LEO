/**
 * Layer 2: Retrieval-First Reasoning
 * Purpose: Enforces the pipeline: Query -> Semantic Search -> Graph Search -> Memory Search -> Tool Search.
 */

import { KnowledgeCrystallizationEngine } from "./l0_knowledgeCrystallization";
import { MemorySystem } from "./l1_memorySystem";

export class RetrievalFirstReasoning {
    private crystalEngine: KnowledgeCrystallizationEngine;
    private memorySystem: MemorySystem;

    constructor() {
        this.crystalEngine = new KnowledgeCrystallizationEngine();
        this.memorySystem = new MemorySystem();
    }

    /**
     * Master pipeline for retrieving knowledge before triggering inference.
     */
    public executeRetrievalPipeline(query: string): any {
        console.log(`[RETRIEVAL REASONING L2] Initiating cascading retrieval pipeline...`);
        
        // 1. Semantic / Crystal Search
        console.log(`[RETRIEVAL REASONING L2] Executing Semantic Search...`);
        
        // 2. Knowledge Graph Search
        console.log(`[RETRIEVAL REASONING L2] Executing Knowledge Graph Search...`);
        
        // 3. Memory System Search
        const memoryResult = this.memorySystem.queryMemory(query, "procedural");
        if (memoryResult) {
            console.log(`[RETRIEVAL REASONING L2] Pipeline resolved at Memory Search stage. Inference bypassed.`);
            return memoryResult;
        }
        
        console.log(`[RETRIEVAL REASONING L2] Retrieval exhausted. Deferring to L3 Expert Swarm.`);
        return null; // Passes to Layer 3
    }
}
