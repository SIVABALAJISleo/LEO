export class VectorMath {
    static dotProduct(a: Float32Array, b: Float32Array): number {
        if (a.length !== b.length) throw new Error('Vector length mismatch');

        let sum = 0;
        for (let i = 0; i < a.length; i++) {
            sum += a[i] * b[i];
        }
        return sum;
    }

    static norm(v: Float32Array): number {
        let sum = 0;
        for (let i = 0; i < v.length; i++) {
            sum += v[i] * v[i];
        }
        return Math.sqrt(sum);
    }

    static cosineSimilarity(a: Float32Array, b: Float32Array): number {
        const dot = this.dotProduct(a, b);
        const normA = this.norm(a);
        const normB = this.norm(b);
        return dot / (normA * normB);
    }

    static add(a: Float32Array, b: Float32Array): Float32Array {
        const result = new Float32Array(a.length);
        for (let i = 0; i < a.length; i++) {
            result[i] = a[i] + b[i];
        }
        return result;
    }

    static scale(v: Float32Array, scalar: number): Float32Array {
        const result = new Float32Array(v.length);
        for (let i = 0; i < v.length; i++) {
            result[i] = v[i] * scalar;
        }
        return result;
    }
}
