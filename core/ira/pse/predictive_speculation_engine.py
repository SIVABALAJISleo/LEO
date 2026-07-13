"""
Predictive Speculation Engine (PSE).
Executes speculative decoding by pairing a lightweight draft model on Intel iGPU
with a larger main model running on CPU.
"""
import time
import os
import threading
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

import openvino as ov
from transformers import AutoTokenizer

from core.ira.shared.config import PSEConfig
from core.ira.shared.logging import IRALogger
from core.ira.shared.metrics import get_metric_collector
from core.ira.shared.timing import PrecisionTimer
from core.ira.shared.exceptions import ModelLoadError, SpeculationError

@dataclass
class SpeculationResult:
    accepted_tokens: List[int]
    draft_tokens: List[int]
    verification_probs: List[np.ndarray]
    draft_probs: List[float]
    draft_time_ms: float
    verify_time_ms: float
    rejected_at: Optional[int] = None

class PredictiveSpeculationEngine:
    def __init__(self, config: PSEConfig = None):
        self.config = config or PSEConfig()
        
        self.draft_model = None
        self.main_model = None
        self.tokenizer = None
        self._models_loaded = False
        
        self.logger = IRALogger.get_logger("pse")
        self.metrics = get_metric_collector().system.get_or_create_pillar("pse")
        
        # Statistics
        self.total_draft_tokens = 0
        self.total_accepted_tokens = 0
        self.total_speculation_rounds = 0
        self.total_verification_time_ms = 0.0
        self.total_draft_time_ms = 0.0

    def load_models(self) -> None:
        """Loads draft model on GPU/iGPU and main model on CPU using OpenVINO."""
        if self._models_loaded:
            return
            
        load_error = None
        
        def do_load():
            nonlocal load_error
            try:
                core = ov.Core()
                available_devices = core.available_devices
                self.logger.info(f"Available OpenVINO devices: {available_devices}")
                
                # 4. Determine draft_device (GPU / iGPU preferred)
                draft_device = "CPU"
                if self.config.draft_device == "GPU" and "GPU" in available_devices:
                    draft_device = "GPU"
                else:
                    self.logger.warning("Intel GPU not found. Falling back to CPU for draft speculation.")
                    
                # 5. Determine main_device (CPU preferred)
                main_device = "CPU"
                if self.config.main_device in available_devices:
                    main_device = self.config.main_device
                else:
                    main_device = available_devices[0]
                    
                draft_path = os.path.join(self.config.draft_model_path, "model.xml")
                main_path = os.path.join(self.config.main_model_path, "model.xml")
                
                if not os.path.exists(draft_path):
                    raise FileNotFoundError(f"Draft model file not found: {draft_path}")
                if not os.path.exists(main_path):
                    raise FileNotFoundError(f"Main model file not found: {main_path}")
                    
                # 6. Load draft model
                self.logger.info(f"Reading draft model from {draft_path}...")
                draft_ov_model = core.read_model(draft_path)
                self.logger.info(f"Compiling draft model on {draft_device}...")
                self.draft_model = core.compile_model(draft_ov_model, device_name=draft_device, config={
                    "PERFORMANCE_HINT": "LATENCY",
                    "NUM_STREAMS": "1"
                })
                
                # 7. Load main model
                self.logger.info(f"Reading main model from {main_path}...")
                main_ov_model = core.read_model(main_path)
                self.logger.info(f"Compiling main model on {main_device}...")
                self.main_model = core.compile_model(main_ov_model, device_name=main_device, config={
                    "PERFORMANCE_HINT": "LATENCY",
                    "CPU_THREADS_NUM": str(self.config.main_threads),
                    "NUM_STREAMS": "1"
                })
                
                # 8. Load tokenizer
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(self.config.draft_model_path)
                except Exception:
                    try:
                        self.tokenizer = AutoTokenizer.from_pretrained(self.config.main_model_path)
                    except Exception:
                        self.logger.warning("Tokenizer not found at paths. Falling back to default gpt2.")
                        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
                        
                self._models_loaded = True
                self.logger.info("Draft and Main models successfully loaded into OpenVINO runtime.")
            except Exception as e:
                load_error = e

        load_thread = threading.Thread(target=do_load)
        load_thread.start()
        load_thread.join(timeout=30.0)
        
        if load_thread.is_alive():
            raise ModelLoadError("Model loading operation timed out (30 seconds limit).", self.config.draft_model_path, "timeout", "pse")
            
        if load_error:
            raise ModelLoadError(f"Failed to compile models in OpenVINO: {load_error}", self.config.draft_model_path, str(load_error), "pse")

    def _ensure_loaded(self) -> None:
        if not self._models_loaded:
            self.load_models()

    def speculate_and_verify(self, prompt_tokens: List[int],
                           temperature: float = None) -> SpeculationResult:
        self._ensure_loaded()
        temp = temperature if temperature is not None else self.config.temperature
        
        # 1. Draft Generate
        draft_timer = PrecisionTimer("draft_generate").start()
        draft_tokens, draft_probs = self._draft_generate(prompt_tokens, self.config.speculation_length, temp)
        draft_time_ms = draft_timer.stop()
        self.total_draft_time_ms += draft_time_ms
        self.total_draft_tokens += len(draft_tokens)
        
        # 2. Main Verify
        verify_timer = PrecisionTimer("verify_batch").start()
        full_tokens = prompt_tokens + draft_tokens
        verification_probs = self._verify_batch(full_tokens, len(draft_tokens))
        verify_time_ms = verify_timer.stop()
        self.total_verification_time_ms += verify_time_ms
        self.total_speculation_rounds += 1
        
        # 3. Acceptance evaluation
        accepted_tokens = []
        rejected_at = None
        
        for i, draft_token in enumerate(draft_tokens):
            main_prob = verification_probs[i][draft_token]
            draft_prob = draft_probs[i]
            
            # Speculative Acceptance Criteria:
            acceptance_prob = min(1.0, main_prob / max(0.001, draft_prob))
            r = np.random.uniform(0.0, 1.0)
            
            if r < acceptance_prob:
                accepted_tokens.append(draft_token)
            else:
                rejected_at = i
                break
                
        self.total_accepted_tokens += len(accepted_tokens)
        
        return SpeculationResult(
            accepted_tokens=accepted_tokens,
            draft_tokens=draft_tokens,
            verification_probs=verification_probs,
            draft_probs=draft_probs,
            draft_time_ms=draft_time_ms,
            verify_time_ms=verify_time_ms,
            rejected_at=rejected_at
        )

    def _draft_generate(self, tokens: List[int], num_tokens: int,
                        temperature: float) -> Tuple[List[int], List[float]]:
        # Simulate draft token generation using compile models
        # Or mock inference if models are loaded (real execution)
        draft_generated = []
        draft_probs = []
        
        current_tokens = list(tokens)
        for _ in range(num_tokens):
            # Form standard input tensor
            input_data = np.array([current_tokens], dtype=np.int64)
            # Invoke compiled draft model
            # Inputs to OpenVINO are mapped via model input signatures
            inputs = {self.draft_model.inputs[0]: input_data}
            results = self.draft_model(inputs)
            # Find output logit vector (last position)
            logits = list(results.values())[0][0, -1, :]
            
            # Softmax with temperature
            probs = self._apply_temperature(logits, temperature)
            next_token = self._top_p_sample(probs, self.config.top_p)
            
            draft_generated.append(next_token)
            draft_probs.append(probs[next_token])
            current_tokens.append(next_token)
            
        return draft_generated, draft_probs

    def _verify_batch(self, all_tokens: List[int],
                      verify_count: int) -> List[np.ndarray]:
        input_data = np.array([all_tokens], dtype=np.int64)
        inputs = {self.main_model.inputs[0]: input_data}
        results = self.main_model(inputs)
        
        logits = list(results.values())[0][0, :, :] # (seq_len, vocab_size)
        
        # Get logits for the speculative positions (last verify_count positions before final output)
        seq_len = len(all_tokens)
        start_idx = seq_len - verify_count - 1
        
        verification_probs = []
        for i in range(start_idx, seq_len - 1):
            probs = self._apply_temperature(logits[i, :], self.config.temperature)
            verification_probs.append(probs)
            
        return verification_probs

    def _generate_single_token(self, tokens: List[int],
                               temperature: float) -> int:
        input_data = np.array([tokens], dtype=np.int64)
        inputs = {self.main_model.inputs[0]: input_data}
        results = self.main_model(inputs)
        logits = list(results.values())[0][0, -1, :]
        probs = self._apply_temperature(logits, temperature)
        return self._top_p_sample(probs, self.config.top_p)

    def generate_with_speculation(self, prompt: str, max_tokens: int = 256,
                                  temperature: float = None) -> Tuple[str, dict]:
        self._ensure_loaded()
        temp = temperature if temperature is not None else self.config.temperature
        
        prompt_tokens = self.tokenizer.encode(prompt)
        all_tokens = list(prompt_tokens)
        prompt_len = len(prompt_tokens)
        
        start_time = time.perf_counter()
        
        while (len(all_tokens) - prompt_len) < max_tokens:
            res = self.speculate_and_verify(all_tokens, temp)
            all_tokens.extend(res.accepted_tokens)
            
            if res.rejected_at is not None:
                # Corrective single generation from main model
                next_token = self._generate_single_token(all_tokens, temp)
                all_tokens.append(next_token)
                
                # Check for EOS
                if next_token == self.tokenizer.eos_token_id:
                    break
            else:
                # Check if last token of fully accepted batch was EOS
                if all_tokens[-1] == self.tokenizer.eos_token_id:
                    break
                    
        total_time = time.perf_counter() - start_time
        gen_tokens = len(all_tokens) - prompt_len
        tokens_per_sec = gen_tokens / max(0.001, total_time)
        
        stats = {
            "total_draft_tokens": self.total_draft_tokens,
            "total_accepted_tokens": self.total_accepted_tokens,
            "acceptance_rate": self.acceptance_rate,
            "effective_speedup": self.effective_speedup,
            "tokens_per_sec": tokens_per_sec,
            "total_time_seconds": total_time
        }
        
        response_text = self.tokenizer.decode(all_tokens[prompt_len:])
        return response_text, stats

    def _apply_temperature(self, logits: np.ndarray,
                           temperature: float) -> np.ndarray:
        logits = logits / max(0.01, temperature)
        # Numerical stability shift
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)

    def _top_p_sample(self, probs: np.ndarray, top_p: float) -> int:
        sorted_idx = np.argsort(probs)[::-1]
        sorted_probs = probs[sorted_idx]
        cumsum = np.cumsum(sorted_probs)
        
        # Determine top_p threshold cutoff
        cutoff = np.where(cumsum >= top_p)[0][0]
        truncated_probs = sorted_probs[:cutoff + 1]
        truncated_probs = truncated_probs / np.sum(truncated_probs)
        
        sample = np.random.choice(cutoff + 1, p=truncated_probs)
        return int(sorted_idx[sample])

    def unload_models(self) -> None:
        self.draft_model = None
        self.main_model = None
        self._models_loaded = False
        self.logger.info("Unloaded models to clear RAM.")

    @property
    def is_loaded(self) -> bool:
        return self._models_loaded

    @property
    def acceptance_rate(self) -> float:
        return self.total_accepted_tokens / max(1, self.total_draft_tokens)

    @property
    def effective_speedup(self) -> float:
        return self.acceptance_rate * self.config.speculation_length

    def get_stats(self) -> dict:
        return {
            "total_draft_tokens": self.total_draft_tokens,
            "total_accepted_tokens": self.total_accepted_tokens,
            "total_speculation_rounds": self.total_speculation_rounds,
            "acceptance_rate": self.acceptance_rate,
            "effective_speedup": self.effective_speedup,
            "total_draft_time_ms": self.total_draft_time_ms,
            "total_verification_time_ms": self.total_verification_time_ms
        }
