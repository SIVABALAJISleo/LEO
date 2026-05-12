/**
 * HyperLogLog (HLL) for cardinality estimation (counting unique items)
 * with constant memory.
 */
class HyperLogLog {
    constructor(p = 12) {
        this.p = p;
        this.m = 1 << p; // Number of registers
        this.registers = new Uint8Array(this.m);
    }

    _hash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0; // Convert to 32bit integer
        }
        return hash >>> 0; // Unsigned
    }

    _rho(val) {
        if (val === 0) return 32;
        let p = 1;
        while (((val >> (p - 1)) & 1) === 0) p++;
        return p;
    }

    add(item) {
        const x = this._hash(item);
        const j = x >>> (32 - this.p);
        const w = x << this.p;
        this.registers[j] = Math.max(this.registers[j], this._rho(w));
    }

    count() {
        let Z = 0;
        for (let i = 0; i < this.m; i++) {
            Z += Math.pow(2, -this.registers[i]);
        }

        const alpha = 0.7213 / (1 + 1.079 / this.m);
        let estimate = alpha * this.m * this.m * (1 / Z);

        if (estimate <= 2.5 * this.m) {
            let V = 0;
            for (let i = 0; i < this.m; i++) {
                if (this.registers[i] === 0) V++;
            }
            if (V > 0) {
                estimate = this.m * Math.log(this.m / V);
            }
        }

        return Math.floor(estimate);
    }
}

export { HyperLogLog };
