/**
 * Behavioral Emulation Layer
 * Replaces expensive simulation with learned state transitions and heuristics.
 */

export interface StateTransition {
  from: string;
  to: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  condition: (context: any) => boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  action?: (context: any) => void;
}

export interface BehaviorRule {
  id: string;
  priority: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  condition: (state: any) => boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  outcome: any;
}

export class BehavioralEmulator {
  private static instance: BehavioralEmulator;
  private transitions: StateTransition[] = [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private lookupTables = new Map<string, Map<string, any>>();
  private rules: BehaviorRule[] = [];

  private constructor() {}

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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  addLookupTable(name: string, table: Map<string, any>): void {
    this.lookupTables.set(name, table);
  }

  /**
   * Query lookup table instead of computing
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
