/**
 * Perceptual Validation Metric
 * SSIM-like quality scoring to stop computation when perceptually equivalent.
 */

export interface ValidationResult {
    score: number; // 0-1, higher is better
    isAcceptable: boolean;
    metrics: {
        structural?: number;
        luminance?: number;
        contrast?: number;
        semantic?: number;
    };
}

export class PerceptualValidator {
    private static instance: PerceptualValidator;
    private readonly ACCEPTABLE_THRESHOLD = 0.85;

    private constructor() { }

    static getInstance(): PerceptualValidator {
        if (!PerceptualValidator.instance) {
            PerceptualValidator.instance = new PerceptualValidator();
        }
        return PerceptualValidator.instance;
    }

    /**
     * Compute SSIM-like similarity between two images/data
     */
    validate(
        reference: Float32Array,
        candidate: Float32Array,
        width: number,
        height: number
    ): ValidationResult {
        if (reference.length !== candidate.length) {
            throw new Error('Data size mismatch');
        }

        const structural = this.computeStructural(reference, candidate);
        const luminance = this.computeLuminance(reference, candidate);
        const contrast = this.computeContrast(reference, candidate);

        // Weighted combination (similar to SSIM)
        const score = (structural + luminance + contrast) / 3;

        return {
            score,
            isAcceptable: score >= this.ACCEPTABLE_THRESHOLD,
            metrics: {
                structural,
                luminance,
                contrast
            }
        };
    }

    /**
     * Fast perceptual comparison (simpler than full SSIM)
     */
    fastCompare(a: Float32Array, b: Float32Array): number {
        let sumDiff = 0;
        let sumRef = 0;

        for (let i = 0; i < a.length; i++) {
            const diff = Math.abs(a[i] - b[i]);
            sumDiff += diff * diff;
            sumRef += a[i] * a[i];
        }

        const mse = sumDiff / a.length;
        const psnr = 10 * Math.log10(1.0 / (mse + 1e-10));

        // Normalize to 0-1
        return Math.min(1.0, psnr / 40); // 40dB is excellent
    }

    private computeStructural(a: Float32Array, b: Float32Array): number {
        // Simplified correlation
        let correlation = 0;
        for (let i = 0; i < a.length; i++) {
            correlation += a[i] * b[i];
        }
        return Math.min(1.0, correlation / a.length);
    }

    private computeLuminance(a: Float32Array, b: Float32Array): number {
        let sumA = 0, sumB = 0;
        for (let i = 0; i < a.length; i++) {
            sumA += a[i];
            sumB += b[i];
        }
        const meanA = sumA / a.length;
        const meanB = sumB / b.length;
        return 1.0 - Math.min(1.0, Math.abs(meanA - meanB));
    }

    private computeContrast(a: Float32Array, b: Float32Array): number {
        // Variance comparison
        let varA = 0, varB = 0;
        let sumA = 0, sumB = 0;

        for (let i = 0; i < a.length; i++) {
            sumA += a[i];
            sumB += b[i];
        }

        const meanA = sumA / a.length;
        const meanB = sumB / b.length;

        for (let i = 0; i < a.length; i++) {
            varA += (a[i] - meanA) ** 2;
            varB += (b[i] - meanB) ** 2;
        }

        return 1.0 - Math.min(1.0, Math.abs(Math.sqrt(varA) - Math.sqrt(varB)));
    }

    /**
     * Semantic difference for non-visual data
     */
    semanticDiff(a: string, b: string): number {
        // Levenshtein-like distance, normalized
        const maxLen = Math.max(a.length, b.length);
        if (maxLen === 0) return 1.0;

        let distance = 0;
        for (let i = 0; i < maxLen; i++) {
            if (a[i] !== b[i]) distance++;
        }

        return 1.0 - (distance / maxLen);
    }
}
