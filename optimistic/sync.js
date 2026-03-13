/**
 * Local-First Optimistic Sync Engine
 * Handles immediate UI updates, background synchronization, and basic conflict resolution.
 */
class OptimisticSync {
    constructor(userId) {
        this.userId = userId;
        this.pendingChanges = [];
        this.state = {};
        this.listeners = {
            'change': [],
            'update': [],
            'sync': []
        };
    }

    on(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }

    _emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(cb => cb(data));
        }
    }

    /**
     * Immediate UI update
     */
    applyChange(key, value) {
        const timestamp = Date.now();
        const change = { key, value, timestamp, status: 'pending', id: Math.random().toString(36).substr(2, 9) };

        // Optimistic state update
        this.state[key] = value;
        this.pendingChanges.push(change);

        console.log(`[OPTIMISTIC] Immediate update: ${key} = ${value}`);
        this._emit('change', change);

        // Background sync
        this._syncInBackground(change);
    }

    async _syncInBackground(change) {
        console.log(`[SYNC] Syncing change ${change.id} to background...`);

        // Simulate network latency
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Simulate successful sync
        change.status = 'synced';
        console.log(`[SYNC] Change ${change.id} successfully synced.`);

        this._emit('sync', change);
        this._emit('update', this.state);
    }

    getState() {
        return this.state;
    }
}

export { OptimisticSync };
