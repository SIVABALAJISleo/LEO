/**
 * Module J: Unknowns Framework
 * Purpose: Convert ignorance into research.
 */

export interface ResearchQueueItem {
    id: string;
    gapDetected: string;
    priority: "LOW" | "MEDIUM" | "HIGH";
    status: "queued" | "in_progress" | "resolved";
}

export class UnknownsEngine {
    private researchQueue: ResearchQueueItem[] = [];

    /**
     * Maps an identified knowledge gap into an actionable research queue item.
     * Rule: Never answer with certainty when certainty is unavailable.
     */
    public convertIgnoranceToResearch(gapDescription: string): ResearchQueueItem {
        console.log(`[UNKNOWNS ENGINE] Knowledge gap mapped: ${gapDescription}`);
        
        const task: ResearchQueueItem = {
            id: `research-${Date.now()}`,
            gapDetected: gapDescription,
            priority: "HIGH",
            status: "queued"
        };
        
        this.researchQueue.push(task);
        console.log(`[UNKNOWNS ENGINE] Research task queued. Queue size: ${this.researchQueue.length}`);
        
        return task;
    }

    public getQueue(): ResearchQueueItem[] {
        return this.researchQueue;
    }
}
