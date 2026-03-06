import { useState, useCallback, useRef } from 'react';
import { api } from '@/hooks/useBackendInitialization';

export type JobStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface JobResult {
    job_id: string;
    job_type: string;
    status: JobStatus;
    result?: unknown;
    error?: string;
}

export function useJobPolling() {
    const [isPolling, setIsPolling] = useState(false);
    const [currentJobId, setCurrentJobId] = useState<string | null>(null);
    const pollIntervalRef = useRef<number | null>(null);

    const stopPolling = useCallback(() => {
        if (pollIntervalRef.current) {
            window.clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
        }
        setIsPolling(false);
        setCurrentJobId(null);
    }, []);

    const startPolling = useCallback(
        (jobId: string, onComplete: (result: JobResult) => void, onError: (err: Error | unknown) => void) => {
            setCurrentJobId(jobId);
            setIsPolling(true);

            const poll = async () => {
                try {
                    const response = await api.get(`/api/v1/jobs/${jobId}`);
                    const jobData = response.data as JobResult;

                    if (jobData.status === 'completed' || jobData.status === 'failed') {
                        stopPolling();
                        if (jobData.status === 'completed') {
                            onComplete(jobData);
                        } else {
                            onError(new Error(jobData.error || 'Job failed'));
                        }
                    }
                } catch (error) {
                    stopPolling();
                    onError(error);
                }
            };

            // Poll every 2 seconds
            pollIntervalRef.current = window.setInterval(poll, 2000);
            poll(); // Immediate first check
        },
        [stopPolling]
    );

    return { startPolling, stopPolling, isPolling, currentJobId };
}
