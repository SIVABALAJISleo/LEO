// LEO AI V33 — Mamba Evaluation Engine
// Capabilities: Compute sequence model throughput, token generation latency, and linear memory scaling.

export interface ScalingBenchmark {
  sequenceLength: number;
  transformerFlops: number;
  mambaFlops: number;
  transformerMemoryBytes: number;
  mambaMemoryBytes: number;
  speedRatio: number; // Mamba throughput / Transformer throughput
}

export class MambaEvaluationEngine {
  runScalingBenchmark(lengths: number[] = [1024, 2048, 4096, 8192, 16384, 32768, 65536]): ScalingBenchmark[] {
    const hiddenSize = 2048;
    const numLayers = 24;

    return lengths.map(len => {
      // Transformer Attention: 2 * seq_len^2 * hidden_size * num_layers FLOPS for attention matrix
      // Plus feed-forward and projection blocks.
      const transformerAttentionFlops = 2 * len * len * hiddenSize * numLayers;
      const baseFeedForwardFlops = 12 * len * hiddenSize * hiddenSize * numLayers;
      const transformerFlops = transformerAttentionFlops + baseFeedForwardFlops;

      // Mamba linear scaling: no seq_len^2 attention matrix!
      // Recurrent state transition and convolution: O(N) complexity
      const mambaScanFlops = 2 * len * hiddenSize * 16 * numLayers; // d_state=16
      const mambaFlops = baseFeedForwardFlops + mambaScanFlops;

      // Memory usage (approximate in bytes)
      // Transformer stores key-value cache: 2 * 2 * num_layers * hidden_size * seq_len * precision (float16 = 2 bytes)
      const transformerMemoryBytes = 2 * 2 * numLayers * hiddenSize * len * 2;
      // Mamba stores fixed size recurrence states: num_layers * hidden_size * d_state * precision
      const mambaMemoryBytes = numLayers * hiddenSize * 16 * 2;

      const speedRatio = parseFloat((transformerFlops / mambaFlops).toFixed(2));

      return {
        sequenceLength: len,
        transformerFlops,
        mambaFlops,
        transformerMemoryBytes,
        mambaMemoryBytes,
        speedRatio,
      };
    });
  }
}
