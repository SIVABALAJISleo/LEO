#include "linter_compat.h"
#include <iostream>
#include <cstdlib>

using namespace std;

/**
 * PRIME-FACTOR SEMANTIC ENGINE (GSF-CORE)
 * Core Philosophy: Fundamental Theorem of Arithmetic
 * 
 * CORE PRINCIPLE: 
 * "Semantic combinations are unique products of prime tokens."
 */

typedef __uint128_t u128; // Using 128-bit for larger semantic space
typedef uint64_t u64;

class PrimeEngine {
private:
    std::map<std::string, u64> prime_map;
    
public:
    PrimeEngine() {
        // Initialize base concepts with primes
        // In production, this dictionary is precompiled and shared
        prime_map["status"] = 2;
        prime_map["check"] = 3;
        prime_map["alpha"] = 5;
        prime_map["beta"] = 7;
        prime_map["gamma"] = 11;
        prime_map["reboot"] = 13;
        prime_map["shutdown"] = 17;
        prime_map["system"] = 19;
    }

    // Commutative Semantic Key Generation
    u128 compute_product(const std::vector<std::string>& tokens) {
        u128 product = 1;
        for (const auto& t : tokens) {
            auto it = prime_map.find(t);
            if (it != prime_map.end()) {
                product *= it->second;
            }
        }
        return product;
    }
    
    // Hash function for CDN mapping
    // We'll use a simple representation for the demo
    std::string get_hex_hash(u128 product) {
        char buf[64];
        u64 high = (u64)(product >> 64);
        u64 low = (u64)product;
        snprintf(buf, 64, "%016llx%016llx", (unsigned long long)high, (unsigned long long)low);
        return std::string(buf);
    }
};

// --- WASM INTERFACE ---
extern "C" {
    PrimeEngine* global_gsf = nullptr;

    const char* generate_gsf_key(const char* space_separated_tokens) {
        if (!global_gsf) global_gsf = new PrimeEngine();
        
        std::vector<std::string> tokens;
        char* copy = strdup(space_separated_tokens);
        char* token = strtok(copy, " ");
        while (token) {
            tokens.push_back(token);
            token = strtok(NULL, " ");
        }
        
        u128 product = global_gsf->compute_product(tokens);
        std::string hex = global_gsf->get_hex_hash(product);
        
        std::free(copy);
        return strdup(hex.c_str()); // Recipient must free
    }
}

// Local testing
int main() {
    PrimeEngine engine;
    
    // Test Commutativity
    u128 p1 = engine.compute_product({"check", "system", "status"});
    u128 p2 = engine.compute_product({"status", "system", "check"});
    
    std::cout << "Product 1: " << engine.get_hex_hash(p1) << std::endl;
    std::cout << "Product 2: " << engine.get_hex_hash(p2) << std::endl;
    
    if (p1 == p2) std::cout << "SUCCESS: Commutative Match." << std::endl;
    
    return 0;
}
