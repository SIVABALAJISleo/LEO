export interface LogEntry {
    id: number;
    timestamp: number;
    operation: string;
    payload: any;
    synced: boolean;
}

export class WriteAheadLogger {
    private static instance: WriteAheadLogger;
    private logs: LogEntry[] = [];
    private currentId: number = 0;

    private constructor() { }

    static getInstance(): WriteAheadLogger {
        if (!WriteAheadLogger.instance) {
            WriteAheadLogger.instance = new WriteAheadLogger();
        }
        return WriteAheadLogger.instance;
    }

    log(operation: string, payload: any): number {
        const entry: LogEntry = {
            id: ++this.currentId,
            timestamp: Date.now(),
            operation,
            payload,
            synced: false
        };
        this.logs.push(entry);

        // Simulating persistent write
        console.log(`[WAL] Appended entry ${entry.id}: ${operation}`);

        return entry.id;
    }

    async recover(): Promise<LogEntry[]> {
        console.log('[WAL] Initiating recovery sequence...');
        const unsynced = this.logs.filter(l => !l.synced);
        console.log(`[WAL] Found ${unsynced.length} unsynced operations to replay.`);
        return unsynced;
    }

    markSynced(id: number) {
        const log = this.logs.find(l => l.id === id);
        if (log) log.synced = true;
    }
}
