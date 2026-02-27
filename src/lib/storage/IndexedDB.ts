import Dexie, { Table } from 'dexie';

export interface SyncItem {
    id: string;
    key: string;
    value: any;
    status: 'pending' | 'synced' | 'conflict';
    timestamp: number;
}

export class HyperDB extends Dexie {
    syncQueue!: Table<SyncItem>;

    constructor() {
        super('HyperDB');
        this.version(1).stores({
            syncQueue: 'id, key, status, timestamp'
        });
    }
}

export const db = new HyperDB();
