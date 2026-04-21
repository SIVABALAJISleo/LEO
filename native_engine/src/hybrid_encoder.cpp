#include <cstdint>
#include <cstring>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>

using namespace std;

/**
 * HYBRID SEMANTIC ENCODER (V7)
 * SIMD-Ready SPM (Symbolic Pattern Mapping) + SimHash-64
 * 
 * CORE PRINCIPLE: 
 * "Deterministic color-coding of semantics. Identity over Approximation."
 */

typedef uint64_t u64;

class HybridEncoder {
private:
    // FNV-1a for token colorization (SPM)
    u64 fnv1a(const std::string& s) {
        u64 hash = 0xcbf29ce484222325ULL;
        for (char c : s) {
            hash ^= (u64)c;
            hash *= 0x100000001b3ULL;
        }
        return hash;
    }

public:
    // Generates a 64-bit deterministic 'Semantic Color'
    u64 encode(const std::string& input) {
        std::vector<int> bits(64, 0);
        std::stringstream ss(input);
        std::string token;
        
        while (ss >> token) {
            u64 color = fnv1a(token);
            for (int i = 0; i < 64; ++i) {
                if ((color >> i) & 1) bits[i]++;
                else bits[i]--;
            }
        }

        u64 fingerprint = 0;
        for (int i = 0; i < 64; ++i) {
            if (bits[i] > 0) fingerprint |= (1ULL << i);
        }
        return fingerprint;
    }

    // Fast Hamming distance for candidate filtering
    static int distance(u64 h1, u64 h2) {
        u64 x = h1 ^ h2;
        int dist = 0;
        while (x > 0) {
            if (x & 1) dist++;
            x >>= 1;
        }
        return dist;
    }
};

// --- WASM INTERFACE ---
extern "C" {
    HybridEncoder* global_encoder = nullptr;

    uint64_t get_semantic_key(const char* text) {
        if (!global_encoder) global_encoder = new HybridEncoder();
        return global_encoder->encode(text);
    }

    int get_semantic_distance(uint64_t h1, uint64_t h2) {
        return HybridEncoder::distance(h1, h2);
    }
}
