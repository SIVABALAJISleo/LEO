import { useState, useEffect } from 'react';
import { db, SyncItem } from '../lib/storage/IndexedDB';
import { v4 as uuidv4 } from 'uuid';
import { toast } from 'sonner';

export const useOptimisticSync = (endpoint: string) => {
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'error'>('idle');

    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const performAction = async (key: string, value: any) => {
        const item: SyncItem = {
            id: uuidv4(),
            key,
            value,
            status: 'pending',
            timestamp: Date.now(),
        };

        // 1. Update UI immediately (optimistic) - handled by caller or local state
        // 2. Persist to IndexedDB
        await db.syncQueue.add(item);

        toast.success("Action saved locally");

        if (isOnline) {
            triggerSync();
        }
    };

    const triggerSync = async () => {
        const pending = await db.syncQueue.where('status').equals('pending').toArray();
        if (pending.length === 0) return;

        setSyncStatus('syncing');
        try {
            for (const item of pending) {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item),
                });

                if (response.ok) {
                    await db.syncQueue.update(item.id, { status: 'synced' });
                } else {
                    // Conflict or Error
                    await db.syncQueue.update(item.id, { status: 'conflict' });
                    toast.error(`Sync conflict for ${item.key}`);
                }
            }
            setSyncStatus('idle');
        } catch (error) {
            setSyncStatus('error');
            logger.error("sync_failed", error);
        }
    };

    return { performAction, isOnline, syncStatus, triggerSync };
};

// Simple logger mock if not available in TS context
const logger = {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    error: (msg: string, err: any) => console.error(`[Sync] ${msg}`, err)
};
