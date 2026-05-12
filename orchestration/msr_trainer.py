import json
import random
import os

"""
MSR TRAINER - 500 SAMPLE GENERATOR
Generates a diverse training set for the Micro Semantic Resolver.
"""

class MSRTrainer:
    def __init__(self):
        self.domains = {
            "CONTROL": {
                "verbs": ["reboot", "restart", "shutdown", "stop", "start", "initialize", "reset", "kill", "activate"],
                "targets": ["alpha node", "beta node", "primary engine", "core reactor", "cooling system", "power grid", "uplink", "subsystem delta"],
                "mods": ["now", "immediately", "safely", "at once", "with high priority", "after verification"]
            },
            "INFO": {
                "verbs": ["how is", "check", "report", "show", "status of", "health of", "metrics for", "telemetry from"],
                "targets": ["system", "load", "temperature", "bandwidth", "memory", "storage", "uptime", "latency", "node alpha", "node beta"],
                "mods": ["all", "overall", "locally", "summary", "detailed"]
            },
            "SYSTEM": {
                "verbs": ["update", "synchronize", "backup", "restore", "patch", "verify", "audit", "index"],
                "targets": ["registry", "log files", "identity table", "semantic database", "version", "build", "manifest"],
                "mods": ["silently", "in background", "forcefully"]
            }
        }

    def generate_samples(self, count=500):
        samples = []
        for i in range(count):
            domain = random.choice(list(self.domains.keys()))
            d = self.domains[domain]
            
            verb = random.choice(d["verbs"])
            target = random.choice(d["targets"])
            mod = random.choice(d["mods"]) if random.random() > 0.5 else ""
            
            query = f"{verb} {target} {mod}".strip()
            
            samples.append({
                "id": f"{domain}_{i:03d}",
                "query": query,
                "domain": domain,
                "response": f"Resolution: Accessing {domain} for '{target}'. Action: {verb}.",
                "tags": [domain.lower(), target.split()[-1]]
            })
        return samples

    def build_naive_bayes_model(self, samples):
        """
        Builds a tiny token-probability table.
        P(Domain | Token)
        """
        token_domain_counts = {}
        domain_counts = {"CONTROL": 0, "INFO": 0, "SYSTEM": 0}
        
        for s in samples:
            domain = s["domain"]
            domain_counts[domain] += 1
            tokens = set(s["query"].lower().split())
            for t in tokens:
                if t not in token_domain_counts:
                    token_domain_counts[t] = {"CONTROL": 0, "INFO": 0, "SYSTEM": 0}
                token_domain_counts[t][domain] += 1
                
        # Convert to probabilities (likelihoods)
        model = {
            "token_probs": {},
            "priors": {d: count/len(samples) for d, count in domain_counts.items()}
        }
        
        for t, counts in token_domain_counts.items():
            # Only keep tokens that actually help differentiate
            # (Remove very common or very rare tokens to keep model <200kb)
            if sum(counts.values()) < 2: continue
            
            model["token_probs"][t] = {d: c / domain_counts[d] for d, c in counts.items()}
            
        print(f"Naive Bayes Model Built: {len(model['token_probs'])} features.")
        return model

if __name__ == "__main__":
    trainer = MSRTrainer()
    samples = trainer.generate_samples(500)
    
    # Save the huge dataset
    with open("msr_dataset_500.json", "w") as f:
        json.dump(samples, f, indent=2)
        
    # Save the NB model
    model = trainer.build_naive_bayes_model(samples)
    with open("msr_nb_model.json", "w") as f:
        json.dump(model, f, indent=2)
        
    print(f"Generated 500 samples and NB model. Total JSON size: {os.path.getsize('msr_nb_model.json') // 1024} KB")
