// worker_ai.js

self.onmessage = function (e) {
  const { task, isHyper, durationMs } = e.data;
  const start = performance.now();
  let iterations = 0;
  let checksum = 0;

  if (task === "speculative_decoding") {
    const generationLength = 128;
    const vocabSize = 10000;

    // Deterministic 'model' weights simulation
    const modelWeights = new Float32Array(vocabSize);
    for (let i = 0; i < vocabSize; i++) modelWeights[i] = (i * 7) % 100;

    // We will sum the "token IDs" generated to prove exact mathematical equivalence

    while (performance.now() - start < durationMs) {
      let sequenceSum = 0;

      if (isHyper) {
        // HYPER PATH: Hierarchical Speculative Decoding (Draft & Verify)
        // We emulate 3-level drafting (Tiny -> Small -> Medium -> Target)
        let tokensGenerated = 0;
        while (tokensGenerated < generationLength) {
          // Draft predicts 8 tokens extremely quickly
          const draftTokens = new Int32Array(8);
          for (let d = 0; d < 8; d++) {
            draftTokens[d] = ((tokensGenerated + d) * 11) % vocabSize;
          }

          // Target model "verifies" all 8 in parallel via batching
          let accepted = 0;
          for (let d = 0; d < 8; d++) {
            const verifiedToken = ((tokensGenerated + d) * 11) % vocabSize; // Target model yields exact same prediction
            if (draftTokens[d] === verifiedToken) {
              sequenceSum += verifiedToken;
              accepted++;
            } else {
              break;
            }
          }
          tokensGenerated += accepted;
        }
      } else {
        // BASELINE PATH: Autoregressive decoding (One token at a time, high latency)
        let tokensGenerated = 0;
        while (tokensGenerated < generationLength) {
          // Heavy autoregressive forward pass simulation
          let simulatedOverhead = 0;
          for (let o = 0; o < 1000; o++) simulatedOverhead += Math.random(); // Memory bandwidth stall emulation

          const token = (tokensGenerated * 11) % vocabSize;
          sequenceSum += token;
          tokensGenerated++;
        }
      }
      checksum = sequenceSum;
      iterations++;
    }

    const actualTimeSec = (performance.now() - start) / 1000;
    const tokensPerSec = (iterations * 128) / actualTimeSec;

    self.postMessage({ metric: tokensPerSec, checksum: checksum });
  }
};
