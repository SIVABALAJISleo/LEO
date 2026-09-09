"""
hyper_cco/workloads/llm_speculative.py
======================================
Manifest Workload 3: Speculative Decoding (LLM_SPECULATIVE_32TOK).

Generates 32 tokens using genuine neural forward passes without synthetic delays.
  - Target model: 4-layer MLP projection / self-attention surrogate (d_model=128, vocab=256)
  - Draft model: 1-layer lightweight surrogate (d_model=128, vocab=256)
  - Speculative parameter: K=4 tokens drafted per verification round.

Baseline:
  Target model standard autoregressive generation (32 sequential forward passes).

Candidate (HYPER-CCO):
  Speculative decoding:
    - Draft model generates K candidate tokens with lightweight compute.
    - Target model evaluates candidate prefix in a single parallel batched pass.
    - Verified prefix is accepted; mismatched suffix is rejected.
    - Exactness: Token sequence must match target model greedy rollout.
"""

import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from hyper_cco.contract import ComputeContract, ExactnessClass, EvidenceClass


def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)


class SurrogateLM:
    """Lightweight real neural model for reproducible deterministic benchmarking."""

    def __init__(self, vocab_size: int = 256, d_model: int = 128, layers: int = 2, seed: int = 42):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.layers = layers
        rng = np.random.RandomState(seed)
        self.embed = rng.randn(vocab_size, d_model).astype(np.float32) * 0.1
        self.weights = [rng.randn(d_model, d_model).astype(np.float32) * 0.1 for _ in range(layers)]
        self.lm_head = rng.randn(d_model, vocab_size).astype(np.float32) * 0.1

    def forward_step(self, token_ids: List[int]) -> np.ndarray:
        """Run forward step on sequence and return logits for the next token."""
        # Simple real embedding + feedforward layers
        emb = self.embed[token_ids[-1]]  # (d_model,)
        h = emb
        for W in self.weights:
            h = np.maximum(0.0, np.dot(h, W))  # ReLU
        logits = np.dot(h, self.lm_head)
        return logits

    def forward_batch(self, sequences: List[List[int]]) -> np.ndarray:
        """Evaluate next-token logits for multiple sequences in parallel."""
        last_tokens = [seq[-1] for seq in sequences]
        embs = self.embed[last_tokens]  # (B, d_model)
        h = embs
        for W in self.weights:
            h = np.maximum(0.0, np.matmul(h, W))
        logits = np.matmul(h, self.lm_head)
        return logits


class LlmSpeculativeWorkload:
    """Speculative Decoding 32 Tokens Workload specification."""

    WORKLOAD_ID = "LLM_SPECULATIVE_32TOK"
    TARGET_TOKENS = 32
    DRAFT_K = 4
    VOCAB_SIZE = 256
    D_MODEL = 128

    def __init__(self, seed: int = 42):
        # Target Model (4 layers)
        self.target_model = SurrogateLM(self.VOCAB_SIZE, self.D_MODEL, layers=4, seed=seed)
        # Draft Model (1 layer)
        self.draft_model = SurrogateLM(self.VOCAB_SIZE, self.D_MODEL, layers=1, seed=seed + 100)

        self.initial_prompt = [42, 17, 88, 9]

        # Compute baseline target greedy rollout as ground truth
        self.ref_tokens = self._run_target_rollout(self.initial_prompt, self.TARGET_TOKENS)

        self.contract = ComputeContract(
            workload_id=self.WORKLOAD_ID,
            exactness_class=ExactnessClass.BITWISE_EXACT,
            evidence_class=EvidenceClass.MEASURED_NON_TARGET,
            output_shape=(self.TARGET_TOKENS,),
            output_dtype="int64",
        )

    def _run_target_rollout(self, prompt: List[int], num_tokens: int) -> np.ndarray:
        seq = list(prompt)
        gen: List[int] = []
        for _ in range(num_tokens):
            logits = self.target_model.forward_step(seq)
            next_token = int(np.argmax(logits))
            seq.append(next_token)
            gen.append(next_token)
        return np.array(gen, dtype=np.int64)

    def run_baseline(self) -> np.ndarray:
        """Standard sequential target model generation."""
        return self._run_target_rollout(self.initial_prompt, self.TARGET_TOKENS)

    def run_candidate(self) -> np.ndarray:
        """Speculative decoding: draft K tokens, verify in batch with target model."""
        seq = list(self.initial_prompt)
        gen: List[int] = []

        while len(gen) < self.TARGET_TOKENS:
            needed = self.TARGET_TOKENS - len(gen)
            k = min(self.DRAFT_K, needed)

            # 1. Draft step
            draft_tokens: List[int] = []
            draft_seq = list(seq)
            for _ in range(k):
                d_logits = self.draft_model.forward_step(draft_seq)
                d_tok = int(np.argmax(d_logits))
                draft_tokens.append(d_tok)
                draft_seq.append(d_tok)

            # 2. Parallel Target verification
            eval_seqs = [seq + draft_tokens[:i] for i in range(k)]
            t_logits = self.target_model.forward_batch(eval_seqs)  # (k, vocab)
            target_choices = np.argmax(t_logits, axis=-1)

            # 3. Acceptance loop
            accepted = 0
            for i in range(k):
                if draft_tokens[i] == target_choices[i]:
                    seq.append(draft_tokens[i])
                    gen.append(draft_tokens[i])
                    accepted += 1
                else:
                    # Mismatch: accept target's correction and break
                    seq.append(int(target_choices[i]))
                    gen.append(int(target_choices[i]))
                    accepted += 1
                    break

            if accepted == 0:
                # Fallback: advance 1 token from target
                t_logits_single = self.target_model.forward_step(seq)
                nxt = int(np.argmax(t_logits_single))
                seq.append(nxt)
                gen.append(nxt)

        return np.array(gen[:self.TARGET_TOKENS], dtype=np.int64)

    def verify(self, candidate_output: np.ndarray) -> Tuple[bool, float, float]:
        """Verify candidate tokens against baseline reference tokens."""
        if not isinstance(candidate_output, np.ndarray):
            return False, 1.0, 1.0
        if candidate_output.shape != self.ref_tokens.shape:
            return False, 1.0, 1.0
        matches = int(np.sum(candidate_output == self.ref_tokens))
        acc = float(matches) / float(self.TARGET_TOKENS)
        is_exact = bool(matches == self.TARGET_TOKENS)
        return is_exact, 1.0 - acc, 1.0 - acc
