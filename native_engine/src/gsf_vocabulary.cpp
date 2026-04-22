#include "linter_compat.h"

using namespace std;

/**
 * GSF VOCABULARY ENGINE (V2)
 * Deterministic Semantic Prime-Factorization
 * 
 * CORE PRINCIPLE: 
 * "Synonyms share primes. Combinations are immutable products."
 */

typedef __uint128_t u128; // Using 128-bit for collision-free product space

class GSFVocabulary {
private:
    std::map<std::string, uint64_t> synonym_map;
    std::set<std::string> known_concepts;

public:
    GSFVocabulary() {
        // Grouping synonyms to prime IDs
        _bind({"profit", "earnings", "income", "margin"}, 2);
        _bind({"loss", "deficit", "shortfall"}, 3);
        _bind({"q1", "first quarter"}, 5);
        _bind({"q2", "second quarter"}, 7);
        _bind({"q3", "third quarter"}, 11);
        _bind({"q4", "fourth quarter"}, 13);
        _bind({"status", "check", "report"}, 17);
        _bind({"system", "core", "engine"}, 19);
    }

    void _bind(std::vector<std::string> words, uint64_t prime) {
        for (const auto& w : words) {
            synonym_map[w] = prime;
            known_concepts.insert(w);
        }
    }

    uint64_t get_prime(const std::string& word) {
        auto it = synonym_map.find(word);
        if (it != synonym_map.end()) return it->second;
        return 0; // Unknown
    }

    // Multiply prime IDs into a semantic key
    u128 compute_key(const std::vector<std::string>& tokens) {
        u128 product = 1;
        int count = 0;
        for (const auto& t : tokens) {
            if (count >= 8) break; // Hard limit: 8 tokens
            uint64_t p = get_prime(t);
            if (p > 0) {
                product *= p;
                count++;
            }
        }
        return product;
    }
};

// --- WASM INTERFACE ---
extern "C" {
    GSFVocabulary* global_vocab = nullptr;

    uint64_t resolve_prime(const char* word) {
        if (!global_vocab) global_vocab = new GSFVocabulary();
        return global_vocab->get_prime(word);
    }

    void get_hex_product(const char* space_tokens, char* out_hex) {
        if (!global_vocab) global_vocab = new GSFVocabulary();
        
        std::vector<std::string> tokens;
        char* copy = strdup(space_tokens);
        char* t = strtok(copy, " ");
        while (t) {
            tokens.push_back(t);
            t = strtok(NULL, " ");
        }

        u128 p = global_vocab->compute_key(tokens);
        uint64_t hi = (uint64_t)(p >> 64);
        uint64_t lo = (uint64_t)p;
        sprintf(out_hex, "%016llx%016llx", (long long)hi, (long long)lo);
        free(copy);
    }
}
