export class ChaosMonkey {
    private static instance: ChaosMonkey;
    private enabled: boolean = false;
    private failureRate: number = 0.1;

    private constructor() { }

    static getInstance(): ChaosMonkey {
        if (!ChaosMonkey.instance) {
            ChaosMonkey.instance = new ChaosMonkey();
        }
        return ChaosMonkey.instance;
    }

    setEnabled(enabled: boolean) {
        this.enabled = enabled;
    }

    // Call this at start of critical functions to potentially throw error
    checkFate() {
        if (this.enabled && Math.random() < this.failureRate) {
            const failures = [
                "Network timeout",
                "Service unavailable",
                "Database connection lost",
                "Compute node unresponsive"
            ];
            const reason = failures[Math.floor(Math.random() * failures.length)];
            console.warn(`[ChaosMonkey] unleashed: ${reason}`);
            throw new Error(`[CHAOS] ${reason}`);
        }
    }
}
