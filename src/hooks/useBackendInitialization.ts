// FIX: Added missing 'api' export that JobsPage.tsx requires

import { useState, useEffect } from 'react';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

// ── The 'api' object JobsPage.tsx was trying to import ────────────────────────
export const api = {
    get: async (endpoint: string) => {
        const token = localStorage.getItem('auth_token');
        const res = await fetch(`${BASE_URL}${endpoint}`, {
            headers: {
                'Authorization': token ? `Bearer ${token}` : '',
                'Content-Type': 'application/json',
            },
        });
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
    },

    post: async (endpoint: string, body: unknown) => {
        const token = localStorage.getItem('auth_token');
        const res = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': token ? `Bearer ${token}` : '',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
    },
};

// ── Backend status hook ───────────────────────────────────────────────────────
interface BackendStatus {
    isReady: boolean;
    isLoading: boolean;
    error: string | null;
}

export function useBackendInitialization(): BackendStatus {
    const [status, setStatus] = useState<BackendStatus>({
        isReady: false,
        isLoading: true,
        error: null,
    });

    useEffect(() => {
        let cancelled = false;

        const checkHealth = async () => {
            try {
                await api.get('/health');
                if (!cancelled) setStatus({ isReady: true, isLoading: false, error: null });
            } catch (err) {
                if (!cancelled) setStatus({
                    isReady: false,
                    isLoading: false,
                    error: 'Backend unavailable',
                });
            }
        };

        checkHealth();
        return () => { cancelled = true; };
    }, [],);

    return status;
}

export default useBackendInitialization;
