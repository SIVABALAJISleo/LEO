#include "linter_compat.h"

#ifdef __clang__
// Direct stubs for clangd when linter_compat.h fails to propagate types
namespace std {
    template<typename T1, typename T2> struct pair { T1 first; T2 second; };
    template<typename T> class vector {
    public:
        vector(size_t n, T val = T()) {}
        T& operator[](size_t);
        size_t size() const;
    };
    class string {
    public:
        string() {}
        string(const char*) {}
        bool empty() const { return true; }
        size_t length() const { return 0; }
        string& operator+=(char) { return *this; }
        string& operator+=(int) { return *this; }
        bool operator==(const string&) const { return true; }
    };
    class stringstream {
    public:
        stringstream(const string&) {}
        bool operator>>(string&) { return false; }
        operator bool() const { return false; }
    };
}
#endif

using namespace std;

/**
 * HIGH-PERFORMANCE SIMHASH ROUTING ENGINE - CLIENT CORE
 * 
 * "Approximate routing + strict validation = fast AND reliable"
 */

typedef uint64_t u64;

class SimHashRouter {
private:
    // Simple FNV-1a for token hashing
    u64 fnv1a(const std::string& s) {
        u64 hash = 0xcbf29ce484222325ULL;
        for (char c : s) {
            hash ^= (u64)c;
            hash *= 0x100000001b3ULL;
        }
        return hash;
    }

    bool is_noise(const std::string& s) {
        static const char* noise[] = {"the", "a", "an", "is", "are", "do", "how", "what", "of", "in", "on"};
        for (const char* n : noise) {
            if (s == n) return true;
        }
        return false;
    }

public:
    // 64-bit SimHash with token weighting
    u64 compute_hash(const std::string& input) {
        // 1. Normalization & Tokenization
        std::vector<int> v(64, 0);
        std::stringstream ss(input);
        std::string token;
        
        while (ss >> token) {
            // Lowercase and trim punctuation (simplified)
            std::string clean;
            for (char c : token) {
                if (c >= 'A' && c <= 'Z') clean += (c + ('a' - 'A'));
                else if (c >= 'a' && c <= 'z') clean += c;
                else if (c >= '0' && c <= '9') clean += c;
            }
            
            if (clean.empty() || is_noise(clean)) continue;

            u64 hash = fnv1a(clean);
            int weight = clean.length() > 5 ? 2 : 1; // Basic weighting

            for (int i = 0; i < 64; ++i) {
                if ((hash >> i) & 1) v[i] += weight;
                else v[i] -= weight;
            }
        }

        u64 fingerprint = 0;
        for (int i = 0; i < 64; ++i) {
            if (v[i] > 0) fingerprint |= (1ULL << i);
        }
        return fingerprint;
    }
};

// --- WASM EXPORTS ---
extern "C" {
    SimHashRouter* global_router = nullptr;

    uint64_t get_routing_hash(const char* text) {
        if (!global_router) global_router = new SimHashRouter();
        return global_router->compute_hash(text);
    }
}

int main() {
    SimHashRouter router;
    const char* tests[] = {
        "What is the system status?",
        "Check system health",
        "How do I reboot the alpha node",
        "reboot alpha node"
    };

    for (auto test : tests) {
        printf("Query: '%s' -> Hash: 0x%016llx\n", test, (unsigned long long)router.compute_hash(test));
    }
    return 0;
}
