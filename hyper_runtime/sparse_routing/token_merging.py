import numpy as np

class TokenMerger:
    """
    Implements Token Merging (ToMe) logic to reduce sequence length dynamically.
    Merges highly similar tokens based on cosine similarity, reducing downstream attention complexity.
    """
    def __init__(self, merge_ratio: float = 0.2):
        self.merge_ratio = merge_ratio # Proportion of tokens to merge
        
    def _normalize(self, v: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(v, axis=-1, keepdims=True)
        norms[norms == 0] = 1.0
        return v / norms

    def merge_tokens(self, hidden_states: np.ndarray) -> tuple[np.ndarray, float]:
        """
        Merges similar tokens in the sequence.
        hidden_states shape: [batch_size, seq_len, hidden_dim]
        Returns: 
        - merged_states: [batch_size, new_seq_len, hidden_dim]
        - reduction_ratio: float
        """
        batch_size, seq_len, hidden_dim = hidden_states.shape
        num_to_merge = int(seq_len * self.merge_ratio)
        
        if num_to_merge == 0 or seq_len <= 2:
            return hidden_states, 0.0
            
        merged_states_list = []
        
        for b in range(batch_size):
            states = hidden_states[b]
            norm_states = self._normalize(states)
            
            # Simple bipartite matching simulation (adjacent token similarity for simplicity)
            # In true ToMe, this is done via bipartite soft matching across sets.
            sims = np.sum(norm_states[:-1] * norm_states[1:], axis=-1)
            
            # Find top num_to_merge highest similarities
            merge_indices = np.argsort(-sims)[:num_to_merge]
            merge_indices_set = set(merge_indices)
            
            new_states = []
            i = 0
            while i < seq_len:
                if i in merge_indices_set:
                    # Merge token i and i+1 (average them)
                    merged = (states[i] + states[i+1]) / 2.0
                    new_states.append(merged)
                    i += 2 # Skip next
                else:
                    new_states.append(states[i])
                    i += 1
            
            merged_states_list.append(np.array(new_states))
            
        # For simplicity in this mock, pad back to dense array or handle ragged.
        # Since merged length might vary per batch item in this simple loop, we'll pad to max length
        # In a real transformer, we'd pack them or just return ragged.
        # Here we just assume batch_size=1 or uniform merging for API simplicity.
        max_len = max(len(s) for s in merged_states_list)
        padded_merged = np.zeros((batch_size, max_len, hidden_dim), dtype=np.float32)
        for b, s in enumerate(merged_states_list):
            padded_merged[b, :len(s)] = s
            
        reduction_ratio = 1.0 - (max_len / seq_len)
        return padded_merged, float(reduction_ratio)
