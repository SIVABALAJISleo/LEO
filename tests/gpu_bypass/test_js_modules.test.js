import { HyperLogLog } from '../../probabilistic/hll.js';
import { BloomFilter } from '../../probabilistic/bloom.js';
import { expect, test, describe } from 'vitest';

describe('Probabilistic Module Tests', () => {
    test('HyperLogLog unique counting', () => {
        const hll = new HyperLogLog();
        hll.add("user1");
        hll.add("user2");
        hll.add("user1"); // Repeat

        const count = hll.count();
        expect(count).toBeGreaterThanOrEqual(1);
        expect(count).toBeLessThan(5);
    });

    test('Bloom Filter membership', () => {
        const bf = new BloomFilter();
        bf.add("val1");

        expect(bf.check("val1")).toBe(true);
        expect(bf.check("val2")).toBe(false);
    });
});
