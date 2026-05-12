class SpeculativeDecoder:
    def __init__(self, target_model, draft_model, k=4):
        self.target = target_model
        self.draft = draft_model
        self.k = k
        
    def generate(self, input_ids, max_tokens=20):
        current_ids = input_ids.copy()
        generated = 0
        accepted_total = 0
        
        while generated < max_tokens:
            draft_ids = self.draft.speculate(current_ids, self.k)
            target_logits = self.target.forward(current_ids + draft_ids)
            
            accepted_count = 0
            for i in range(self.k):
                expected = draft_ids[i]
                actual = target_logits[i].argmax()
                if expected == actual:
                    accepted_count += 1
                else:
                    break
                    
            tokens_to_add = draft_ids[:accepted_count] + [target_logits[accepted_count].argmax()]
            current_ids.extend(tokens_to_add)
            
            generated += len(tokens_to_add)
            accepted_total += accepted_count
            
        return current_ids, accepted_total
