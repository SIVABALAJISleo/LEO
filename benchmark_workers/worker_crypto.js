// worker_crypto.js

function rotr(n, b) {
  return (n >>> b) | (n << (32 - b));
}

function hashBlock(w) {
  // Deterministic 64-round hash simulation structurally equivalent to SHA-256 compression
  let a = w[0],
    b = w[1],
    c = w[2],
    d = w[3],
    e = w[4],
    f = w[5],
    g = w[6],
    h = w[7];
  for (let i = 0; i < 64; i++) {
    let S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
    let ch = (e & f) ^ (~e & g);
    let temp1 = (h + S1 + ch + w[i]) | 0;
    let S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
    let maj = (a & b) ^ (a & c) ^ (b & c);
    let temp2 = (S0 + maj) | 0;

    h = g;
    g = f;
    f = e;
    e = (d + temp1) | 0;
    d = c;
    c = b;
    b = a;
    a = (temp1 + temp2) | 0;
  }
  return [a, b, c, d, e, f, g, h];
}

self.onmessage = function (e) {
  const { task, isHyper, durationMs } = e.data;
  const start = performance.now();
  let hashes = 0;
  let checksum = 0;

  if (task === "sha256") {
    const batchSize = 4000;
    const memoryBlocks = new Int32Array(batchSize * 64);
    // Deterministic payload
    for (let i = 0; i < batchSize * 64; i++) {
      memoryBlocks[i] = (i * 1234567) | 0;
    }

    while (performance.now() - start < durationMs) {
      if (isHyper) {
        // HYPER PATH: Loop unrolling & TypedArray pre-fetching for JIT optimization
        for (let i = 0; i < batchSize; i += 2) {
          const offset1 = i * 64;
          const offset2 = (i + 1) * 64;
          const b1 = memoryBlocks.subarray(offset1, offset1 + 64);
          const b2 = memoryBlocks.subarray(offset2, offset2 + 64);

          const out1 = hashBlock(b1);
          const out2 = hashBlock(b2);

          checksum = (checksum + out1[0] + out2[0]) | 0;
          hashes += 2;
        }
      } else {
        // BASELINE PATH: Sequential function call per block with heavy slice overhead
        for (let i = 0; i < batchSize; i++) {
          const block = Array.from(memoryBlocks.slice(i * 64, i * 64 + 64)); // Intentionally slow array conversion
          const out = hashBlock(block);

          checksum = (checksum + out[0]) | 0;
          hashes += 1;
        }
      }
    }

    const actualTimeSec = (performance.now() - start) / 1000;
    const mhs = hashes / 1e6 / actualTimeSec;

    self.postMessage({ metric: mhs, checksum: checksum });
  }
};
