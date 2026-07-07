#include "linter_compat.h"

using namespace std;

/**
 * SIMHASH ENGINE (V6)
 * 64-bit Locality-Sensitive Hashing (LSH)
 * 
 * CORE PRINCIPLE: 
 * "Similar phrases generate similar hashes. Distance is Hamming."
 */

typedef uint64_t u64;

class SimHashEngine {
private:
    // Simple 64-bit string hash (FNV-1a variant) for token weights
    u64 fnv1a(const std::string& s) {
        u64 hash = 0xcbf29ce484222325ULL;
        for (char c : s) {
            hash ^= (u64)c;
            hash *= 0x100000001b3ULL;
        }
        return hash;
    }

public:
    u64 compute(const std::string& input) {
        std::vector<int> v(64, 0);
        std::stringstream ss(input);
        std::string token;
        
        while (ss >> token) {
            u64 hash = fnv1a(token);
            for (int i = 0; i < 64; ++i) {
                if ((hash >> i) & 1) v[i]++;
                else v[i]--;
            }
        }

        u64 fingerprint = 0;
        for (int i = 0; i < 64; ++i) {
            if (v[i] > 0) fingerprint |= (1ULL << i);
        }
        return fingerprint;
    }

    static int hamming_distance(u64 h1, u64 h2) {
        u64 x = h1 ^ h2;
        int distance = 0;
        while (x > 0) {
            if (x & 1) distance++;
            x >>= 1;
        }
        return distance;
    }
};

// --- WASM EXPORTS ---
extern "C" {
    SimHashEngine* global_simhash = nullptr;

    uint64_t get_simhash(const char* text) {
        if (!global_simhash) global_simhash = new SimHashEngine();
        return global_simhash->compute(text);
    }

    int get_hamming_distance(uint64_t h1, uint64_t h2) {
        return SimHashEngine::hamming_distance(h1, h2);
    }
}
