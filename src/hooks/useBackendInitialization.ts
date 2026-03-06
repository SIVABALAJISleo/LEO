/**
 * Hook to initialize backend data when user first visits dashboard
 * Ensures user has seeded data and starts background automation
 */

import { useEffect, useRef, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import {
  initializeUserData,
  startBackgroundAutomation,
  stopBackgroundAutomation,
  runQuickHealthCheck,
  generateRealtimeMetrics
} from '@/lib/backendService';
import axios from 'axios';

export const api = {
  get: async (endpoint: string) => {
    const token = localStorage.getItem('auth_token');
    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8005'}${endpoint}`, {
      headers: { 'Authorization': token ? `Bearer ${token}` : '' }
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },
  post: async (endpoint: string, body: unknown) => {
    const token = localStorage.getItem('auth_token');
    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8005'}${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  }
};

interface BackendStatus {
  initialized: boolean;
  loading: boolean;
  error: string | null;
  health: 'healthy' | 'degraded' | 'critical' | 'unknown';
  lastCheck: Date | null;
}

export function useBackendInitialization() {
  const { user } = useAuth();
  const [status, setStatus] = useState<BackendStatus>({
    initialized: false,
    loading: false,
    error: null,
    health: 'unknown',
    lastCheck: null,
  });
  const initAttempted = useRef(false);

  useEffect(() => {
    if (!user) {
      // Reset when user logs out
      initAttempted.current = false;
      setStatus({
        initialized: false,
        loading: false,
        error: null,
        health: 'unknown',
        lastCheck: null,
      });
      stopBackgroundAutomation();
      return;
    }

    // Only attempt initialization once per session
    if (initAttempted.current) return;
    initAttempted.current = true;

    const initialize = async () => {
      setStatus(prev => ({ ...prev, loading: true, error: null }));

      try {
        // Initialize user data
        console.log('[BackendInit] Initializing user data...');
        const initResult = await initializeUserData();

        if (!initResult.success) {
          console.warn('[BackendInit] Initialization warning:', initResult.message);
          // Don't treat as error - user might already have data
        }

        // Run health check
        console.log('[BackendInit] Running health check...');
        const health = await runQuickHealthCheck();

        // Generate fresh metrics
        console.log('[BackendInit] Generating initial metrics...');
        await generateRealtimeMetrics();

        // Start background automation
        startBackgroundAutomation();

        setStatus({
          initialized: true,
          loading: false,
          error: null,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          health: (health?.status as any) || 'unknown',
          lastCheck: new Date(),
        });

        console.log('[BackendInit] Backend initialization complete');
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (error: any) {
        console.error('[BackendInit] Initialization error:', error);
        setStatus({
          initialized: false,
          loading: false,
          error: error.message,
          health: 'unknown',
          lastCheck: null,
        });
      }
    };

    initialize();

    // Cleanup on unmount
    return () => {
      stopBackgroundAutomation();
    };
  }, [user]);

  // Function to manually refresh health status
  const refreshHealth = async () => {
    const health = await runQuickHealthCheck();
    setStatus(prev => ({
      ...prev,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      health: (health?.status as any) || 'unknown',
      lastCheck: new Date(),
    }));
    return health;
  };

  // Function to regenerate metrics on demand
  const refreshMetrics = async () => {
    setStatus(prev => ({ ...prev, loading: true }));
    await generateRealtimeMetrics();
    setStatus(prev => ({ ...prev, loading: false }));
  };

  return {
    ...status,
    refreshHealth,
    refreshMetrics,
  };
}
