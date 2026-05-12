/**
 * LogicSimulator (Pillar 5: Gaming-Style Performance Tricks)
 * Replaces heavy physical simulations with deterministic state machines
 * and perceptual interpolation.
 */
export class LogicSimulator {
    private static instance: LogicSimulator;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private state: Record<string, any> = {};
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private history: Array<{ timestamp: number, state: any }> = [];

    private constructor() { }

    static getInstance(): LogicSimulator {
        if (!LogicSimulator.instance) {
            LogicSimulator.instance = new LogicSimulator();
        }
        return LogicSimulator.instance;
    }

    /**
     * Interpolates between two states for smooth visual transition
     * without real-time physics calculation.
     */
    interpolate(start: number, end: number, alpha: number): number {
        return start + (end - start) * alpha;
    }

    /**
     * Predicts the next state based on simple event-driven logic.
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    predictNextState(current: any, event: string): any {
        // Example: simple state machine transitions
        switch (event) {
            case 'LOAD_INCREASE':
                return { ...current, load: current.load + 10, status: 'strained' };
            case 'RECOVERY':
                return { ...current, load: Math.max(0, current.load - 20), status: 'optimal' };
            default:
                return current;
        }
    }

    /**
     * Records state for timeline replay and authority reconciliation.
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    snapshot(state: any): void {
        this.history.push({ timestamp: Date.now(), state: { ...state } });
        if (this.history.length > 100) this.history.shift();
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    getHistory(): any[] {
        return this.history;
    }
}

export default LogicSimulator;
