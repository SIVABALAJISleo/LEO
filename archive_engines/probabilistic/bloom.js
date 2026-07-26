/**
 * Bloom Filter for membership testing with low memory footprint.
 */
class BloomFilter {
  constructor(size = 1024, hashCount = 3) {
    this.size = size;
    this.hashCount = hashCount;
    this.bitArray = new Uint8Array(Math.ceil(size / 8));
  }

  _hashes(item) {
    const results = [];
    let hash1 = 0;
    for (let i = 0; i < item.length; i++) {
      hash1 = (hash1 << 5) - hash1 + item.charCodeAt(i);
      hash1 |= 0;
    }

    let hash2 = 0;
    for (let i = item.length - 1; i >= 0; i--) {
      hash2 = (hash2 << 5) - hash2 + item.charCodeAt(i);
      hash2 |= 0;
    }

    for (let i = 0; i < this.hashCount; i++) {
      results.push(Math.abs((hash1 + i * hash2) % this.size));
    }
    return results;
  }

  add(item) {
    const indices = this._hashes(item);
    indices.forEach((idx) => {
      this.bitArray[Math.floor(idx / 8)] |= 1 << (idx % 8);
    });
  }

  check(item) {
    const indices = this._hashes(item);
    return indices.every((idx) => {
      return (this.bitArray[Math.floor(idx / 8)] & (1 << (idx % 8))) !== 0;
    });
  }
}

export { BloomFilter };
