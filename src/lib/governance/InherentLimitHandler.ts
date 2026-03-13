/**
 * ═══════════════════════════════════════════════════════════════
 *  INHERENT LIMIT HANDLER — Response Rules for Fundamental Limits
 * ═══════════════════════════════════════════════════════════════
 *  Unknown knowledge     → ask clarification or escalate
 *  Complex reasoning     → break into verified steps
 *  Slow verification     → provisional + confirmed response
 *  Untrusted feedback    → weighted reviewer trust
 *  Novel situation       → collect data before answering
 *  Memory growth         → compress, archive, or delete
 * ═══════════════════════════════════════════════════════════════
 */

import {
    DecisionMode,
    TerminalAction,
    PipelineContext,
} from './types';

export enum InherentLimit {
    UNKNOWN_KNOWLEDGE = 'UNKNOWN_KNOWLEDGE',
    COMPLEX_REASONING = 'COMPLEX_REASONING',
    SLOW_VERIFICATION = 'SLOW_VERIFICATION',
    UNTRUSTED_FEEDBACK = 'UNTRUSTED_FEEDBACK',
    NOVEL_SITUATION = 'NOVEL_SITUATION',
    MEMORY_GROWTH = 'MEMORY_GROWTH',
}

export interface LimitResponse {
    readonly limit: InherentLimit;
    readonly detected: boolean;
    readonly decisionModeOverride: DecisionMode | null;
    readonly terminalActionOverride: TerminalAction | null;
    readonly instruction: string;
}

export class InherentLimitHandler {
    private static instance: InherentLimitHandler;

    // Thresholds
    private readonly NOVELTY_THRESHOLD = 0.3;        // Below this = truly novel
    private readonly COMPLEXITY_THRESHOLD = 500;      // Token length proxy for complexity
    private readonly SLOW_VERIFICATION_MS = 3000;     // 3 seconds

    private constructor() { }

    static getInstance(): InherentLimitHandler {
        if (!InherentLimitHandler.instance) {
            InherentLimitHandler.instance = new InherentLimitHandler();
        }
        return InherentLimitHandler.instance;
    }

    /**
     * Detect and respond to inherent limits in the current pipeline context.
     * Returns all detected limits with their prescribed responses.
     */
    evaluate(ctx: PipelineContext): LimitResponse[] {
        const responses: LimitResponse[] = [];

        // 1. Unknown Knowledge: No memory match AND low novelty score
        if (ctx.noveltyScore < this.NOVELTY_THRESHOLD && !ctx.matchedMemoryId) {
            responses.push({
                limit: InherentLimit.UNKNOWN_KNOWLEDGE,
                detected: true,
                decisionModeOverride: null,
                terminalActionOverride: TerminalAction.ESCALATE,
                instruction: 'Unknown knowledge detected — escalate for clarification',
            });
        }

        // 2. Complex Reasoning: Long input that likely requires multi-step reasoning
        if (ctx.input.payload.length > this.COMPLEXITY_THRESHOLD) {
            responses.push({
                limit: InherentLimit.COMPLEX_REASONING,
                detected: true,
                decisionModeOverride: DecisionMode.DECOMPOSED,
                terminalActionOverride: null,
                instruction: 'Complex reasoning detected — decomposing into verified steps',
            });
        }

        // 3. Novel Situation: New input with no similar history
        if (ctx.noveltyState === 'NEW' && ctx.noveltyScore < 0.5) {
            responses.push({
                limit: InherentLimit.NOVEL_SITUATION,
                detected: true,
                decisionModeOverride: DecisionMode.FULL,
                terminalActionOverride: TerminalAction.LEARN,
                instruction: 'Novel situation — collecting data before answering, tagged for learning',
            });
        }

        return responses;
    }

    /**
     * Check if slow verification should trigger provisional response.
     */
    checkSlowVerification(elapsedMs: number): LimitResponse | null {
        if (elapsedMs > this.SLOW_VERIFICATION_MS) {
            return {
                limit: InherentLimit.SLOW_VERIFICATION,
                detected: true,
                decisionModeOverride: DecisionMode.PROVISIONAL,
                terminalActionOverride: TerminalAction.VERIFY,
                instruction: 'Slow verification detected — issuing provisional response pending confirmation',
            };
        }
        return null;
    }

    /**
     * Handle untrusted feedback.
     */
    evaluateFeedbackTrust(reviewerTrust: number): LimitResponse | null {
        if (reviewerTrust < 0.3) {
            return {
                limit: InherentLimit.UNTRUSTED_FEEDBACK,
                detected: true,
                decisionModeOverride: null,
                terminalActionOverride: TerminalAction.VERIFY,
                instruction: `Untrusted feedback (trust=${reviewerTrust.toFixed(2)}) — weight reduced, requires secondary verification`,
            };
        }
        return null;
    }
}
