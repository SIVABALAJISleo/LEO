/**
 * ═══════════════════════════════════════════════════════════════
 *  SEMANTIC LOGGER — Policy #8: Observability
 * ═══════════════════════════════════════════════════════════════
 *  Log meaning, not events.
 *  {intent, confidence, reliability, decision_state}
 * ═══════════════════════════════════════════════════════════════
 */

import {
    SemanticLogEntry,
    PipelineStage,
    TerminalAction,
} from './types';
import { v4 as uuidv4 } from 'uuid';

export class SemanticLogger {
    private static instance: SemanticLogger;
    private log: SemanticLogEntry[] = [];
    private readonly MAX_LOG_SIZE = 5000;

    private constructor() { }

    static getInstance(): SemanticLogger {
        if (!SemanticLogger.instance) {
            SemanticLogger.instance = new SemanticLogger();
        }
        return SemanticLogger.instance;
    }

    /**
     * Record a semantic event — what the system *meant* to do.
     */
    record(
        intent: string,
        confidence: number,
        reliability: number,
        decisionState: TerminalAction | 'PROCEED',
        domain: string,
        pipelineStage: PipelineStage,
        metadata?: Record<string, unknown>
    ): SemanticLogEntry {
        const entry: SemanticLogEntry = {
            id: uuidv4(),
            intent,
            confidence,
            reliability,
            decisionState,
            domain,
            pipelineStage,
            timestamp: Date.now(),
            metadata,
        };

        this.log.push(entry);

        // Cap log size
        if (this.log.length > this.MAX_LOG_SIZE) {
            this.log = this.log.slice(-Math.floor(this.MAX_LOG_SIZE * 0.8));
        }

        // Console output for development
        const stateIcon = decisionState === 'PROCEED' ? '✓' : '⚠';
        console.log(
            `[GOV:${pipelineStage}] ${stateIcon} ${intent} | ` +
            `conf=${confidence.toFixed(2)} rel=${reliability.toFixed(2)} → ${decisionState}`
        );

        return entry;
    }

    /** Get all entries, optionally filtered by domain or stage */
    query(filters?: {
        domain?: string;
        stage?: PipelineStage;
        since?: number;
        limit?: number;
    }): SemanticLogEntry[] {
        let results = this.log;

        if (filters?.domain) {
            results = results.filter(e => e.domain === filters.domain);
        }
        if (filters?.stage) {
            results = results.filter(e => e.pipelineStage === filters.stage);
        }
        if (filters?.since) {
            results = results.filter(e => e.timestamp >= filters.since!);
        }

        return (filters?.limit ? results.slice(-filters.limit) : results);
    }

    /** Get semantic summary: failure rate, avg confidence, dominant terminal actions */
    getSummary(domain?: string): Record<string, unknown> {
        const entries = domain ? this.log.filter(e => e.domain === domain) : this.log;
        if (entries.length === 0) return { entries: 0 };

        const failures = entries.filter(e => e.decisionState !== 'PROCEED');
        const avgConf = entries.reduce((s, e) => s + e.confidence, 0) / entries.length;
        const avgRel = entries.reduce((s, e) => s + e.reliability, 0) / entries.length;

        const actionCounts: Record<string, number> = {};
        failures.forEach(e => {
            actionCounts[e.decisionState] = (actionCounts[e.decisionState] || 0) + 1;
        });

        return {
            totalEntries: entries.length,
            failureRate: failures.length / entries.length,
            avgConfidence: avgConf,
            avgReliability: avgRel,
            terminalActionBreakdown: actionCounts,
        };
    }

    /** Clear log (for testing) */
    clear(): void {
        this.log = [];
    }
}
