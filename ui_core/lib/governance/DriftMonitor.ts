/**
 * ═══════════════════════════════════════════════════════════════
 *  DRIFT MONITOR — Policy #2: Data Drift Detection
 * ═══════════════════════════════════════════════════════════════
 *  Continuously compare recent inputs vs historical distribution.
 *  If drift detected → tighten thresholds + reduce automation.
 * ═══════════════════════════════════════════════════════════════
 */

import {
    DistributionSnapshot,
    DriftReport,
} from './types';

export class DriftMonitor {
    private static instance: DriftMonitor;
    private historicalDistributions = new Map<string, DistributionSnapshot>();
    private recentWindows = new Map<string, number[][]>(); // domain → recent embeddings
    private readonly DRIFT_THRESHOLD = 0.3;
    private readonly WINDOW_SIZE = 50;

    private constructor() { }

    static getInstance(): DriftMonitor {
        if (!DriftMonitor.instance) {
            DriftMonitor.instance = new DriftMonitor();
        }
        return DriftMonitor.instance;
    }

    /**
     * Record a new input embedding for drift tracking.
     */
    recordInput(domain: string, embedding: number[]): void {
        if (!this.recentWindows.has(domain)) {
            this.recentWindows.set(domain, []);
        }

        const window = this.recentWindows.get(domain)!;
        window.push(embedding);

        // Keep sliding window
        if (window.length > this.WINDOW_SIZE * 2) {
            // Archive first half as "historical"
            const historicalEmbeddings = window.splice(0, this.WINDOW_SIZE);
            this.updateHistorical(domain, historicalEmbeddings);
        }
    }

    /**
     * Check drift for a domain.
     * Returns a DriftReport with score and recommendation.
     */
    checkDrift(domain: string): DriftReport {
        const historical = this.historicalDistributions.get(domain);
        const recent = this.recentWindows.get(domain);

        // Not enough data yet — no drift
        if (!historical || !recent || recent.length < 10) {
            return {
                domain,
                driftScore: 0,
                driftDetected: false,
                recommendation: 'NONE',
                timestamp: Date.now(),
            };
        }

        // Compute distribution of recent window
        const recentDist = this.computeDistribution(recent);

        // Compare using simplified KL-divergence proxy (mean shift + variance ratio)
        const driftScore = this.computeDriftScore(historical, recentDist);

        const driftDetected = driftScore > this.DRIFT_THRESHOLD;
        let recommendation: 'NONE' | 'TIGHTEN' | 'DISABLE' = 'NONE';

        if (driftScore > 0.7) {
            recommendation = 'DISABLE';
        } else if (driftDetected) {
            recommendation = 'TIGHTEN';
        }

        return {
            domain,
            driftScore,
            driftDetected,
            recommendation,
            timestamp: Date.now(),
        };
    }

    /** Check all domains and return reports for drifted ones */
    checkAllDomains(): DriftReport[] {
        const reports: DriftReport[] = [];
        this.recentWindows.forEach((_, domain) => {
            const report = this.checkDrift(domain);
            if (report.driftDetected) {
                reports.push(report);
            }
        });
        return reports;
    }

    // ──────────────────── Private Helpers ────────────────────

    private updateHistorical(domain: string, embeddings: number[][]): void {
        const dist = this.computeDistribution(embeddings);
        const existing = this.historicalDistributions.get(domain);

        if (!existing) {
            this.historicalDistributions.set(domain, dist);
            return;
        }

        // Exponential moving average merge
        const alpha = 0.3; // Weight for new data
        const merged: DistributionSnapshot = {
            mean: existing.mean.map((m, i) =>
                m * (1 - alpha) + (dist.mean[i] || 0) * alpha
            ),
            variance: existing.variance.map((v, i) =>
                v * (1 - alpha) + (dist.variance[i] || 0) * alpha
            ),
            sampleCount: existing.sampleCount + dist.sampleCount,
            windowStart: existing.windowStart,
            windowEnd: Date.now(),
        };

        this.historicalDistributions.set(domain, merged);
    }

    private computeDistribution(embeddings: number[][]): DistributionSnapshot {
        if (embeddings.length === 0) {
            return { mean: [], variance: [], sampleCount: 0, windowStart: Date.now(), windowEnd: Date.now() };
        }

        const dims = embeddings[0].length;
        const mean = new Array(dims).fill(0);
        const variance = new Array(dims).fill(0);

        // Compute mean
        embeddings.forEach(emb => {
            for (let i = 0; i < dims; i++) {
                mean[i] += emb[i] / embeddings.length;
            }
        });

        // Compute variance
        embeddings.forEach(emb => {
            for (let i = 0; i < dims; i++) {
                variance[i] += Math.pow(emb[i] - mean[i], 2) / embeddings.length;
            }
        });

        return {
            mean,
            variance,
            sampleCount: embeddings.length,
            windowStart: Date.now() - 60000,
            windowEnd: Date.now(),
        };
    }

    private computeDriftScore(
        historical: DistributionSnapshot,
        recent: DistributionSnapshot
    ): number {
        if (historical.mean.length === 0 || recent.mean.length === 0) return 0;

        const dims = Math.min(historical.mean.length, recent.mean.length);
        let meanShift = 0;
        let varianceRatio = 0;

        for (let i = 0; i < dims; i++) {
            // Normalized mean shift
            const hStd = Math.sqrt(Math.max(historical.variance[i], 1e-8));
            meanShift += Math.abs(recent.mean[i] - historical.mean[i]) / hStd;

            // Variance ratio (log scale)
            const hVar = Math.max(historical.variance[i], 1e-8);
            const rVar = Math.max(recent.variance[i], 1e-8);
            varianceRatio += Math.abs(Math.log(rVar / hVar));
        }

        // Normalize by dimensions
        meanShift /= dims;
        varianceRatio /= dims;

        // Combined score (0.0–1.0 clamped)
        return Math.min(1.0, (meanShift * 0.6 + varianceRatio * 0.4));
    }
}
