#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <map>

using namespace std;

/**
 * HYBRID PRIME ENGINE (V3)
 * GSF-Core with Integrated Synonym Mapping
 * 
 * CORE PRINCIPLE: 
 * "95% Deterministic Fast Path (Arithmetic) + 5% Fallback Reasoning."
 */

typedef __uint128_t u128;

class HybridPrimeEngine {
private:
    std::map<std::string, uint64_t> vocab;
    
public:
    HybridPrimeEngine() {
        // Base Concepts -> Primes
        // All synonyms point to the same Prime Identity
        _bind({"status", "check", "report", "health"}, 2);
        _bind({"system", "core", "engine", "platform"}, 3);
        _bind({"reboot", "restart", "reset"}, 5);
        _bind({"alpha", "primary", "node0"}, 7);
        _bind({"beta", "secondary", "node1"}, 11);
        _bind({"metrics", "stats", "telemetry"}, 13);
    }

    void _bind(const std::vector<std::string>& synonyms, uint64_t prime) {
        for (const auto& s : synonyms) vocab[s] = prime;
    }

    // Resolves a list of tokens into a Prime Product Key
    u128 compute_key(const std::vector<std::string>& tokens, bool* has_unknowns) {
        u128 product = 1;
        *has_unknowns = false;
        int count = 0;
        
        for (const auto& t : tokens) {
            if (count >= 6) break; // Hard limit: max 6 tokens
            
            auto it = vocab.find(t);
            if (it != vocab.end()) {
                product *= it->second;
                count++;
            } else {
                *has_unknowns = true;
            }
        }
        return (count > 0) ? product : 0;
    }
};

// --- WASM INTERFACE ---
extern "C" {
    HybridPrimeEngine* global_hybrid = nullptr;

    uint64_t compute_gsf_key_low(const char* space_tokens, int* unknown_count) {
        if (!global_hybrid) global_hybrid = new HybridPrimeEngine();
        
        std::vector<std::string> tokens;
        char* copy = strdup(space_tokens);
        char* t = strtok(copy, " ");
        while(t) {
            tokens.push_back(t);
            t = strtok(NULL, " ");
        }

        bool has_u = false;
        u128 key = global_hybrid->compute_key(tokens, &has_u);
        *unknown_count = has_u ? 1 : 0;
        
        free(copy);
        return (uint64_t)key; // Returning low 64 bits for simplicity in this demo
    }
}
