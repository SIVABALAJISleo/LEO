// Probabilistic Data Structures for CPU Optimization

export class HyperLogLog {
    private registers: Uint8Array;
    private readonly m: number; // Number of registers
    private readonly b: number; // Number of bits for register index

    constructor(b: number = 10) { // b=10 -> 1024 registers, roughly 2% error
        this.b = b;
        this.m = 1 << b;
        this.registers = new Uint8Array(this.m);
    }

    add(str: string): void {
        const hash = this.murmurHash3(str);
        const index = hash >>> (32 - this.b); // First b bits
        const w = (hash << this.b) | (1 << (this.b - 1)); // Remaining bits + sentinel
        const rho = this.clz32(w) + 1; // Rank

        if (rho > this.registers[index]) {
            this.registers[index] = rho;
        }
    }

    count(): number {
        let sum = 0;
        let zeros = 0;
        for (let i = 0; i < this.m; i++) {
            sum += Math.pow(2, -this.registers[i]);
            if (this.registers[i] === 0) zeros++;
        }

        const alpha = 0.7213 / (1 + 1.079 / this.m);
        let estimate = alpha * this.m * this.m / sum;

        if (estimate <= 2.5 * this.m) {
            if (zeros > 0) {
                estimate = this.m * Math.log(this.m / zeros);
            }
        }
        return Math.floor(estimate);
    }

    private clz32(x: number): number {
        return Math.clz32 ? Math.clz32(x) : 0; // Simple fallback if not present, though most JS envs have it
    }

    private murmurHash3(str: string): number {
        let h = 0xdeadbeef;
        for (let i = 0; i < str.length; i++) {
            h = Math.imul(h ^ str.charCodeAt(i), 0x5bd1e995);
            h ^= h >>> 15;
            h = Math.imul(h, 0x5bd1e995);
        }
        return h >>> 0;
    }
}

export class BloomFilter {
    private bitArray: Uint8Array;
    private size: number;
    private hashCount: number;

    constructor(expectedItems: number, falsePositiveRate: number = 0.01) {
        this.size = Math.ceil(- (expectedItems * Math.log(falsePositiveRate)) / (Math.log(2) ** 2));
        this.hashCount = Math.ceil((this.size / expectedItems) * Math.log(2));
        this.bitArray = new Uint8Array(Math.ceil(this.size / 8));
    }

    add(str: string): void {
        const hashes = this.getHashes(str);
        hashes.forEach(h => {
            const index = h % this.size;
            this.bitArray[Math.floor(index / 8)] |= (1 << (index % 8));
        });
    }

    has(str: string): boolean {
        const hashes = this.getHashes(str);
        return hashes.every(h => {
            const index = h % this.size;
            return (this.bitArray[Math.floor(index / 8)] & (1 << (index % 8))) !== 0;
        });
    }

    private getHashes(str: string): number[] {
        const hashes = [];
        let h1 = 0xdeadbeef;
        let h2 = 0x41c6ce57;

        for (let i = 0; i < str.length; i++) {
            h1 = Math.imul(h1 ^ str.charCodeAt(i), 2654435761);
            h2 = Math.imul(h2 ^ str.charCodeAt(i), 1597334677);
        }

        for (let i = 0; i < this.hashCount; i++) {
            hashes.push(Math.abs((h1 + i * h2) >>> 0));
        }
        return hashes;
    }
}
