/**
 * src/lib/breakthrough-algorithms/streaming-sketches.ts
 * =============================================================================
 * Genuine In-Browser Streaming Probabilistic Sketches
 * - HyperLogLog (Flajolet et al. 2007) for Cardinality Estimation in O(1) space
 * - Bloom Filter (Bloom 1970) for Sub-millisecond Membership Testing
 * - Count-Min Sketch (Cormode & Muthukrishnan 2005) for Heavy Hitters
 * =============================================================================
 */

/**
 * 32-bit Murmur3-style integer hash function.
 */
export function hash32(val: number | string, seed: number = 0x9747b28c): number {
  const str = typeof val === "string" ? val : String(val);
  let h = seed ^ str.length;
  for (let i = 0; i < str.length; i++) {
    const c = str.charCodeAt(i);
    h = Math.imul(h ^ c, 0x5bd1e995);
    h ^= h >>> 15;
  }
  return h >>> 0;
}

/**
 * HyperLogLog Cardinality Sketch with m = 128 registers (O(1) memory, ~128 bytes).
 */
export class HyperLogLogSketch {
  public m: number;
  public registers: Uint8Array;
  private alphaM: number;

  constructor(m: number = 128) {
    this.m = m;
    this.registers = new Uint8Array(m);
    this.alphaM = 0.7213 / (1 + 1.079 / m);
  }

  public add(item: string | number) {
    const h = hash32(item, 0x12345678);
    const idx = h & (this.m - 1);
    const w = h >>> 7;
    // Count leading zeros of w + 1
    let lz = 1;
    if (w !== 0) {
      let temp = w;
      while ((temp & 0x800000) === 0 && lz < 24) {
        temp <<= 1;
        lz++;
      }
    }
    if (lz > this.registers[idx]) {
      this.registers[idx] = lz;
    }
  }

  public estimate(): number {
    let harmonicSum = 0;
    let zeros = 0;
    for (let j = 0; j < this.m; j++) {
      const reg = this.registers[j];
      harmonicSum += 2.0 ** -reg;
      if (reg === 0) zeros++;
    }

    const rawEstimate = (this.alphaM * this.m * this.m) / harmonicSum;

    // Small range linear counting correction
    if (rawEstimate <= 2.5 * this.m && zeros > 0) {
      return Math.round(this.m * Math.log(this.m / zeros));
    }
    return Math.round(rawEstimate);
  }
}

/**
 * Bloom Filter with k hash functions and m bits.
 */
export class BloomFilterSketch {
  public sizeBits: number;
  public bitArray: Uint8Array;
  public kHashes: number;

  constructor(sizeBits: number = 2048, kHashes: number = 4) {
    this.sizeBits = sizeBits;
    this.bitArray = new Uint8Array(Math.ceil(sizeBits / 8));
    this.kHashes = kHashes;
  }

  public add(item: string | number) {
    for (let i = 0; i < this.kHashes; i++) {
      const h = hash32(item, i * 0x5bd1e995 + 1) % this.sizeBits;
      const byteIdx = h >> 3;
      const bitIdx = h & 7;
      this.bitArray[byteIdx] |= 1 << bitIdx;
    }
  }

  public contains(item: string | number): boolean {
    for (let i = 0; i < this.kHashes; i++) {
      const h = hash32(item, i * 0x5bd1e995 + 1) % this.sizeBits;
      const byteIdx = h >> 3;
      const bitIdx = h & 7;
      if ((this.bitArray[byteIdx] & (1 << bitIdx)) === 0) {
        return false;
      }
    }
    return true; // May have small false positive rate
  }
}

/**
 * Count-Min Sketch for frequency estimation and heavy hitters.
 */
export class CountMinSketch {
  public width: number;
  public depth: number;
  public table: Int32Array;

  constructor(width: number = 256, depth: number = 4) {
    this.width = width;
    this.depth = depth;
    this.table = new Int32Array(width * depth);
  }

  public add(item: string | number, count: number = 1) {
    for (let d = 0; d < this.depth; d++) {
      const h = hash32(item, d * 0x7fed31 + 42) % this.width;
      this.table[d * this.width + h] += count;
    }
  }

  public estimateFrequency(item: string | number): number {
    let minFreq = Infinity;
    for (let d = 0; d < this.depth; d++) {
      const h = hash32(item, d * 0x7fed31 + 42) % this.width;
      const val = this.table[d * this.width + h];
      if (val < minFreq) minFreq = val;
    }
    return minFreq === Infinity ? 0 : minFreq;
  }
}

/**
 * Runs live streaming sketch benchmark.
 */
export function runStreamingSketchBenchmark(streamSize: number = 25000) {
  const hll = new HyperLogLogSketch(128);
  const bloom = new BloomFilterSketch(4096, 4);
  const cms = new CountMinSketch(256, 4);

  const exactSet = new Set<string>();

  const t0 = performance.now();
  for (let i = 0; i < streamSize; i++) {
    // Generate domain keys with Zipfian distribution
    const keyId = Math.floor(10000 * Math.random() ** 2);
    const key = `user_${keyId}`;
    exactSet.add(key);
    hll.add(key);
    bloom.add(key);
    cms.add(key, 1);
  }
  const sketchTimeMs = Math.max(0.01, performance.now() - t0);

  const exactCount = exactSet.size;
  const hllCount = hll.estimate();
  const errorPct = Math.round((Math.abs(hllCount - exactCount) / exactCount) * 1000) / 10;

  return {
    streamSize,
    exactUniqueCardinality: exactCount,
    hllEstimatedCardinality: hllCount,
    hllErrorPercentage: errorPct,
    memoryBytesHll: 128, // 128 bytes vs megabytes of hash maps
    memoryBytesBloom: 512,
    sketchTimeMs: Math.round(sketchTimeMs * 100) / 100,
    contractStatus: errorPct <= 5.0 ? "PASS" : "FAIL",
  };
}
