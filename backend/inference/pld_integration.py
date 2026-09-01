"""
backend/inference/pld_integration.py
====================================
End-to-End Prompt Lookup Speculative Decoding Integration for LEO/HYPER.
Extracts n-gram matches from prompt & retrieved documents without auxiliary model weights,
and verifies proposals against the primary language model in batch verification steps.
"""

from typing import List, Tuple, Generator, Optional, Any, Callable
from core_ai.prompt_lookup_decoder import PromptLookupDecoder


class PLDIntegratedDecoder:
    """
    Integrates Prompt Lookup Decoding with local inference engines.
    """

    def __init__(self, target_engine: Any = None, ngram_size: int = 3, max_proposals: int = 6):
        self.target = target_engine
        self.pld = PromptLookupDecoder(ngram_size=ngram_size, max_proposals=max_proposals)

    def generate_with_pld(
        self,
        prompt: str,
        tokenize_fn: Optional[Callable[[str], List[int]]] = None,
        detokenize_fn: Optional[Callable[[List[int]], str]] = None,
        verify_batch_fn: Optional[Callable[[List[int], List[int]], List[Tuple[bool, int]]]] = None,
        next_token_fn: Optional[Callable[[List[int]], int]] = None,
        max_tokens: int = 128
    ) -> Generator[str, None, None]:
        """
        Generates tokens using speculative prompt lookup verification.
        """
        # Default simple whitespace tokenization if functions are not passed
        tok_fn = tokenize_fn or (lambda s: [hash(w) % 10000 for w in s.split()])
        detok_fn = detokenize_fn or (lambda t: " " + str(t[0]))
        
        tokens = tok_fn(prompt)
        generated_count = 0
        
        while generated_count < max_tokens:
            draft = self.pld.propose_draft_tokens(tokens)
            
            if draft and verify_batch_fn:
                verified = verify_batch_fn(tokens, draft)
                accepted = [t for (ok, t) in verified if ok]
                tokens.extend(accepted)
                generated_count += len(accepted)
                
                for t in accepted:
                    yield detok_fn([t])
                    
                if len(accepted) < len(verified):
                    # Append first rejected token's correction
                    corrected_token = verified[len(accepted)][1]
                    tokens.append(corrected_token)
                    generated_count += 1
                    yield detok_fn([corrected_token])
                    continue
                elif len(accepted) == 0:
                    break
            elif next_token_fn:
                tok = next_token_fn(tokens)
                tokens.append(tok)
                generated_count += 1
                yield detok_fn([tok])
            else:
                # Mock step if no engine attached
                break

    def get_telemetry(self):
        return self.pld.get_telemetry()
