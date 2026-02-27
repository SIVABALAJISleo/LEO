/**
 * Behavioral Emulation Layer
 * Replaces expensive simulation with learned state transitions and heuristics.
 */

export interface StateTransition {
    from: string;
    to: string;
    condition: (context: any) => boolean;
    action?: (context: any) => void;
}

export interface BehaviorRule {
    id: string;
    priority: number;
    condition: (state: any) => boolean;
    outcome: any;
}

export class BehavioralEmulator {
    private static instance: BehavioralEmulator;
    private transitions: StateTransition[] = [];
    private lookupTables = new Map<string, Map<string, any>>();
    private rules: BehaviorRule[] = [];

    private constructor() { }

    static getInstance(): BehavioralEmulator {
        if (!BehavioralEmulator.instance) {
            BehavioralEmulator.instance = new BehavioralEmulator();
        }
        return BehavioralEmulator.instance;
    }

    /**
     * Register state machine transitions
     */
    registerTransition(transition: StateTransition): void {
        this.transitions.push(transition);
    }

    /**
     * Execute state machine step
     */
    step(currentState: string, context: any): string {
        for (const transition of this.transitions) {
            if (transition.from === currentState && transition.condition(context)) {
                transition.action?.(context);
                console.log(`[BehaviorEmulator] ${currentState} → ${transition.to}`);
                return transition.to;
            }
        }
        return currentState;
    }

    /**
     * Add lookup table for precomputed results
     */
    addLookupTable(name: string, table: Map<string, any>): void {
        this.lookupTables.set(name, table);
    }

    /**
     * Query lookup table instead of computing
     */
    lookup(tableName: string, key: string): any | null {
        const table = this.lookupTables.get(tableName);
        return table?.get(key) || null;
    }

    /**
     * Register heuristic rule
     */
    addRule(rule: BehaviorRule): void {
        this.rules.push(rule);
        this.rules.sort((a, b) => b.priority - a.priority);
    }

    /**
     * Evaluate rules to get outcome
     */
    evaluate(state: any): any | null {
        for (const rule of this.rules) {
            if (rule.condition(state)) {
                console.log(`[BehaviorEmulator] Matched rule: ${rule.id}`);
                return rule.outcome;
            }
        }
        return null;
    }
}
