/**
 * ═══════════════════════════════════════════════════════════════
 *  ADVERSARIAL SHIELD — Policy #6: Adversarial Input Rejection
 * ═══════════════════════════════════════════════════════════════
 *  Reject inputs outside normal embedding distance bounds.
 *  Never allow model processing before validation.
 * ═══════════════════════════════════════════════════════════════
 */

export class AdversarialShield {
    private static instance: AdversarialShield;
    private baselineNorms = new Map<string, { mean: number; std: number; count: number }>();
    private readonly ANOMALY_SIGMA = 3.0; // Reject inputs outside 3σ
    private readonly MIN_SAMPLES_FOR_BASELINE = 20;

    private constructor() { }

    static getInstance(): AdversarialShield {
        if (!AdversarialShield.instance) {
            AdversarialShield.instance = new AdversarialShield();
        }
        return AdversarialShield.instance;
    }

    /**
     * Validate an input embedding before any model processing.
     * Returns adversarial score: 0.0 = normal, 1.0 = highly adversarial.
     */
    validate(domain: string, embedding: number[]): {
        score: number;
        accepted: boolean;
        reason: string;
    } {
        // Check 1: Embedding sanity (NaN, Inf, zero-vector)
        const sanityResult = this.checkSanity(embedding);
        if (!sanityResult.valid) {
            return { score: 1.0, accepted: false, reason: sanityResult.reason };
        }

        // Check 2: Norm anomaly detection
        const norm = this.computeNorm(embedding);
        const normResult = this.checkNormAnomaly(domain, norm);

        // Check 3: Entropy check (adversarial inputs often have unusual entropy)
        const entropy = this.computeEntropy(embedding);
        const entropyScore = entropy < 0.1 ? 0.5 : 0.0; // Very low entropy = suspicious

        // Combined score
        const combinedScore = Math.min(1.0, normResult.anomalyScore * 0.7 + entropyScore * 0.3);

        // Update baseline with valid inputs
        if (combinedScore < 0.5) {
            this.updateBaseline(domain, norm);
        }

        return {
            score: combinedScore,
            accepted: combinedScore < 0.7,
            reason: combinedScore >= 0.7
                ? `Adversarial input detected (score=${combinedScore.toFixed(3)}, norm=${norm.toFixed(3)})`
                : 'Input validated',
        };
    }

    // ──────────────────── Private Helpers ────────────────────

    private checkSanity(embedding: number[]): { valid: boolean; reason: string } {
        if (embedding.length === 0) {
            return { valid: false, reason: 'Empty embedding vector' };
        }

        for (let i = 0; i < embedding.length; i++) {
            if (!Number.isFinite(embedding[i])) {
                return { valid: false, reason: `Non-finite value at dimension ${i}` };
            }
        }

        // Zero-vector check
        const norm = this.computeNorm(embedding);
        if (norm < 1e-10) {
            return { valid: false, reason: 'Zero-norm embedding vector' };
        }

        return { valid: true, reason: '' };
    }

    private checkNormAnomaly(
        domain: string,
        norm: number
    ): { anomalyScore: number } {
        const baseline = this.baselineNorms.get(domain);

        // Not enough data for baseline — accept conservatively
        if (!baseline || baseline.count < this.MIN_SAMPLES_FOR_BASELINE) {
            return { anomalyScore: 0.0 };
        }

        // Z-score based anomaly
        const z = Math.abs(norm - baseline.mean) / Math.max(baseline.std, 1e-8);
        const anomalyScore = Math.min(1.0, z / this.ANOMALY_SIGMA);

        return { anomalyScore };
    }

    private updateBaseline(domain: string, norm: number): void {
        const existing = this.baselineNorms.get(domain);

        if (!existing) {
            this.baselineNorms.set(domain, { mean: norm, std: 0, count: 1 });
            return;
        }

        // Welford's online algorithm for running mean and variance
        const n = existing.count + 1;
        const delta = norm - existing.mean;
        const newMean = existing.mean + delta / n;
        const delta2 = norm - newMean;
        const newVariance = (existing.std * existing.std * existing.count + delta * delta2) / n;

        existing.mean = newMean;
        existing.std = Math.sqrt(newVariance);
        existing.count = n;
    }

    private computeNorm(embedding: number[]): number {
        let sum = 0;
        for (let i = 0; i < embedding.length; i++) {
            sum += embedding[i] * embedding[i];
        }
        return Math.sqrt(sum);
    }

    private computeEntropy(embedding: number[]): number {
        // Discretize and compute Shannon entropy
        const bins = 20;
        const counts = new Array(bins).fill(0);
        const min = Math.min(...embedding);
        const max = Math.max(...embedding);
        const range = max - min || 1e-8;

        embedding.forEach(v => {
            const bin = Math.min(bins - 1, Math.floor(((v - min) / range) * bins));
            counts[bin]++;
        });

        let entropy = 0;
        const total = embedding.length;
        counts.forEach(c => {
            if (c > 0) {
                const p = c / total;
                entropy -= p * Math.log2(p);
            }
        });

        // Normalize to 0–1
        return entropy / Math.log2(bins);
    }
}
