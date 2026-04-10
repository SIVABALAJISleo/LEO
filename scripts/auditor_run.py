
import json
import requests
import time

# Simulation of REF_MODEL (Auditor's Reference Knowledge)
REF_ANSWERS = {
    1: "No, all bloops are not necessarily lazies.",
    2: "No, Sue is shorter than John.",
    3: "C is the parent (mother or father) of A.",
    4: "32",
    5: "Not necessarily; there could be other reasons for the grass being wet (e.g., sprinklers).",
    6: "No, animals are not necessarily birds (logical fallacy).",
    7: "No, it is not safe based on the premise.",
    8: "P must be false (Modus Tollens).",
    9: "0.25 or 1/4",
    10: "9",
    11: "The meeting was moved to a later date (tomorrow).",
    12: "She bought a new car.",
    13: "The firm grew a lot last year.",
    14: "Safety protocols must be followed.",
    15: "The teacher distributed the work.",
    16: "He was very tired after running.",
    17: "Rains is expected this weekend.",
    18: "Provide your details.",
    19: "Completed the project needs more assets.",
    20: "I'm eager for our next talk.",
    21: "57",
    22: "$20",
    23: "150 miles",
    24: "10",
    25: "54",
    26: "30",
    27: "256",
    28: "14",
    29: "62.83 (20 * pi)",
    30: "17 (2+3+5+7)",
    31: "When are you going to finish the project?",
    32: "I cannot believe it works so well.",
    33: "Please tell me how to sign in again.",
    34: "Why is the system slow today?",
    35: "Can you help me fix the error?",
    36: "Where is the file I saved yesterday?",
    37: "Is there a way to speed up the process?",
    38: "Thanks for the help, man.",
    39: "I need more information on the next step.",
    40: "What is the best way to use this tool?",
    41: "Paris",
    42: "William Shakespeare",
    43: "Au",
    44: "Mars",
    45: "1945",
    46: "Mount Everest",
    47: "Leonardo da Vinci",
    48: "Pacific Ocean",
    49: "Hydrogen",
    50: "Sir Isaac Newton"
}

def semantic_compare(ref, hyper):
    ref_norm = ref.lower()
    hyper_norm = hyper.lower()
    
    # Simple semantic overlap check for this simulation
    # In a full audit, we'd use a small cross-encoder model
    if ref_norm == hyper_norm:
        return 1.0
    
    # Check for keyword presence
    keywords = [w for w in ref_norm.split() if len(w) > 3]
    matches = sum(1 for k in keywords if k in hyper_norm)
    
    if matches == len(keywords) and len(keywords) > 0:
        return 1.0
    if matches > 0:
        return 0.5
    return 0.0

def run_audit():
    with open("benchmark.json", "r") as f:
        data = json.load(f)
    
    results = []
    total_score = 0
    
    for item in data["benchmark"]:
        qid = item["id"]
        question = item["question"]
        
        # Step A: Get Ref
        answer_ref = REF_ANSWERS.get(qid, "Unknown")
        
        # Step B: Query HYPER (Orchestrate Endpoint)
        try:
            # We use the /api/orchestrate endpoint which handles logic routing
            resp = requests.post("http://localhost:8005/api/orchestrate", json={"query": question}, timeout=5)
            if resp.status_code == 200:
                answer_hyper = resp.json().get("result", "")
            else:
                answer_hyper = "Error: System failed to respond"
        except Exception as e:
            answer_hyper = f"Connection Error: {str(e)}"
            
        # Step C: Compare
        score = semantic_compare(answer_ref, answer_hyper)
        total_score += score
        
        results.append({
            "id": qid,
            "category": item["category"],
            "question": question,
            "answer_ref": answer_ref,
            "answer_hyper": answer_hyper,
            "score": score
        })
        time.sleep(0.1)
        
    final_score = total_score / len(results)
    
    output = {
        "final_score": final_score,
        "results": results,
        "classification": classify(final_score),
        "timestamp": time.time()
    }
    
    with open("results_raw.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Audit Complete. Score: {final_score:.2f}")

def classify(score):
    if score >= 0.90: return "Near-equivalent reasoning engine"
    if score >= 0.70: return "Approximate cognitive engine"
    if score >= 0.40: return "Heuristic automation system"
    return "Rule-based responder"

if __name__ == "__main__":
    run_audit()
