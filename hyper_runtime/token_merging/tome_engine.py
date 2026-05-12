import numpy as np

class TokenMergingRuntime:
    """
    Implements Token Merging (ToMe) for sequence reduction.
    Merges redundant or highly similar tokens using bipartite matching.
    """
    def __init__(self, merge_ratio=0.5):
        self.merge_ratio = merge_ratio
        
    def _cosine_similarity(self, a, b):
        return np.dot(a, b.T) / (np.linalg.norm(a, axis=-1, keepdims=True) * np.linalg.norm(b, axis=-1) + 1e-9)

    def merge_tokens(self, tokens, hidden_states):
        """
        tokens: list of token IDs
        hidden_states: [seq_len, d_model]
        """
        seq_len = hidden_states.shape[0]
        num_to_merge = int(seq_len * self.merge_ratio)
        
        if num_to_merge == 0:
            return tokens, hidden_states
            
        evens = hidden_states[0::2]
        odds = hidden_states[1::2]
        
        sim = self._cosine_similarity(evens, odds)
        flat_indices = np.argsort(sim, axis=None)[::-1]
        
        merged_mask = np.zeros(seq_len, dtype=bool)
        new_hidden = []
        new_tokens = []
        
        for idx in flat_indices[:num_to_merge]:
            even_idx = idx // odds.shape[0]
            odd_idx = idx % odds.shape[0]
            
            real_even = even_idx * 2
            real_odd = odd_idx * 2 + 1
            
            if not merged_mask[real_even] and not merged_mask[real_odd]:
                merged_mask[real_even] = True
                merged_mask[real_odd] = True
                merged_state = (hidden_states[real_even] + hidden_states[real_odd]) / 2.0
                new_hidden.append(merged_state)
                new_tokens.append(f"<{tokens[real_even]}+{tokens[real_odd]}>")
                
        for i in range(seq_len):
            if not merged_mask[i]:
                new_hidden.append(hidden_states[i])
                new_tokens.append(tokens[i])
                
        return new_tokens, np.array(new_hidden)
