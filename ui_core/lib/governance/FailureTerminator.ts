/**
 * ═══════════════════════════════════════════════════════════════
 *  FAILURE TERMINATOR — System Guarantee
 * ═══════════════════════════════════════════════════════════════
 *  Every possible failure path must end in one of:
 *    REFUSE, ESCALATE, VERIFY, LIMIT, or LEARN
 *
 *  Never silent failure. Never uncontrolled output.
 * ═══════════════════════════════════════════════════════════════
 */

import {
    TerminalAction,
    PipelineContext,
    PipelineStage,
} from './types';

export interface TerminationResult {
    readonly action: TerminalAction;
    readonly stage: PipelineStage;
    readonly reason: string;
    readonly recoverable: boolean;
}

export class FailureTerminator {
    private static instance: FailureTerminator;
    private terminationLog: TerminationResult[] = [];
    private readonly MAX_LOG = 1000;

    private constructor() { }

    static getInstance(): FailureTerminator {
        if (!FailureTerminator.instance) {
            FailureTerminator.instance = new FailureTerminator();
        }
        return FailureTerminator.instance;
    }

    /**
     * GUARANTEE: Convert any error into a deterministic terminal action.
     * This is the last-resort handler — every catch block should route here.
     */
    terminate(
        error: unknown,
        context: PipelineContext
    ): TerminationResult {
        const stage = context.currentStage;
        const errorMessage = this.extractError(error);

        // Determine terminal action based on failure type
        const result = this.classifyFailure(errorMessage, stage, context);

        // Log the termination
        this.terminationLog.push(result);
        if (this.terminationLog.length > this.MAX_LOG) {
            this.terminationLog = this.terminationLog.slice(-Math.floor(this.MAX_LOG * 0.8));
        }

        console.error(
            `[FailureTerminator] ${result.action} at ${result.stage}: ${result.reason}`
        );

        return result;
    }

    /**
     * Ensure a pipeline context has a valid terminal action.
     * If it reached the end without one, assign LEARN (the most permissive).
     */
    ensureTermination(context: PipelineContext): TerminalAction {
        if (context.terminalAction) {
            return context.terminalAction;
        }

        // No terminal action and no errors → success path → LEARN for feedback tracking
        if (context.errors.length === 0 && context.result !== null) {
            return TerminalAction.LEARN;
        }

        // Has errors but no terminal action → this should never happen
        // Safety net: REFUSE
        console.error(
            `[FailureTerminator] Pipeline completed with errors but no terminal action. Forcing REFUSE.`
        );
        return TerminalAction.REFUSE;
    }

    /** Get termination statistics */
    getStats(): Record<TerminalAction, number> {
        const stats: Record<string, number> = {
            [TerminalAction.REFUSE]: 0,
            [TerminalAction.ESCALATE]: 0,
            [TerminalAction.VERIFY]: 0,
            [TerminalAction.LIMIT]: 0,
            [TerminalAction.LEARN]: 0,
        };

        this.terminationLog.forEach(t => {
            stats[t.action]++;
        });

        return stats as Record<TerminalAction, number>;
    }

    /** Get recent terminations */
    getRecentTerminations(limit: number = 20): TerminationResult[] {
        return this.terminationLog.slice(-limit);
    }

    // ──────────────────── Private Helpers ────────────────────

    private classifyFailure(
        error: string,
        stage: PipelineStage,
        context: PipelineContext
    ): TerminationResult {
        // Input validation failures → REFUSE
        if (stage === PipelineStage.INPUT || stage === PipelineStage.DOMAIN_CHECK) {
            return {
                action: TerminalAction.REFUSE,
                stage,
                reason: `Input/domain validation failed: ${error}`,
                recoverable: false,
            };
        }

        // Adversarial detection → REFUSE
        if (context.adversarialScore > 0.7) {
            return {
                action: TerminalAction.REFUSE,
                stage,
                reason: `Adversarial input detected (score=${context.adversarialScore.toFixed(3)}): ${error}`,
                recoverable: false,
            };
        }

        // Safety check failures → ESCALATE
        if (stage === PipelineStage.SAFETY_CHECK) {
            return {
                action: TerminalAction.ESCALATE,
                stage,
                reason: `Safety check failed: ${error}`,
                recoverable: true,
            };
        }

        // Authority failures → ESCALATE
        if (stage === PipelineStage.AUTHORITY_CONTROL) {
            return {
                action: TerminalAction.ESCALATE,
                stage,
                reason: `Authority insufficient: ${error}`,
                recoverable: true,
            };
        }

        // Reasoning failures → LIMIT output
        if (stage === PipelineStage.REASONING_MODE) {
            return {
                action: TerminalAction.LIMIT,
                stage,
                reason: `Reasoning failed, output limited: ${error}`,
                recoverable: true,
            };
        }

        // Memory/lifecycle failures → VERIFY (output may still be ok)
        if (stage === PipelineStage.MEMORY_LIFECYCLE) {
            return {
                action: TerminalAction.VERIFY,
                stage,
                reason: `Memory lifecycle error (output may be valid): ${error}`,
                recoverable: true,
            };
        }

        // Unknown failure → REFUSE (safest default)
        return {
            action: TerminalAction.REFUSE,
            stage,
            reason: `Unclassified failure at ${stage}: ${error}`,
            recoverable: false,
        };
    }

    private extractError(error: unknown): string {
        if (error instanceof Error) return error.message;
        if (typeof error === 'string') return error;
        return String(error);
    }
}
