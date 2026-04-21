#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cctype>
#include <vector>
#include <string>
#include <map>

using namespace std;

/**
 * FST CLIENT ENGINE (V5) - WASM TARGET
 * Zero-Backend Compute Semantic Parser
 * 
 * CORE PRINCIPLE: 
 * "Intelligence is precompiled. The runtime is just a lookup."
 */

typedef uint64_t u64;

// Simple Node for Finite State Transducer
struct FSTNode {
    std::map<char, int> transitions;
    u64 terminal_query_id; // 0 if not terminal
};

class FSTParser {
private:
    std::vector<FSTNode> nodes;
    
public:
    FSTParser() {
        // Initialize with Root
        nodes.push_back(FSTNode{ {}, 0 });
    }

    // Offline compilation step (Simulated)
    void compile_intent(const std::string& text, u64 query_id) {
        int current = 0;
        for (char c : text) {
            c = tolower(c);
            if (nodes[current].transitions.find(c) == nodes[current].transitions.end()) {
                nodes[current].transitions[c] = nodes.size();
                nodes.push_back(FSTNode{ {}, 0 });
            }
            current = nodes[current].transitions[c];
        }
        nodes[current].terminal_query_id = query_id;
    }

    // Client-side execution (<1ms)
    u64 parse(const char* input) {
        int current = 0;
        for (const char* p = input; *p; ++p) {
            char c = tolower(*p);
            // Skip spaces/punctuation for simple robust match
            if (c == ' ' || c == '?' || c == '!') continue;
            
            if (nodes[current].transitions.find(c) == nodes[current].transitions.end()) {
                return 0; // Not found
            }
            current = nodes[current].transitions[c];
        }
        return nodes[current].terminal_query_id;
    }
};

// --- WASM EXPORTS ---
extern "C" {
    FSTParser* global_parser = nullptr;

    void init_engine() {
        global_parser = new FSTParser();
        // Precompile fixed intents
        global_parser->compile_intent("status", 1001);
        global_parser->compile_intent("check system", 1002);
        global_parser->compile_intent("how is the engine", 1001); 
        global_parser->compile_intent("reboot alpha", 5001);
    }

    u64 resolve_intent(const char* text) {
        if (!global_parser) return 0;
        return global_parser->parse(text);
    }
}

// For local testing
int main() {
    init_engine();
    const char* test = "Check system!";
    u64 id = resolve_intent(test);
    
    if (id > 0) {
        printf("Parsed '%s' -> QUERY_ID: %llu\n", test, (unsigned long long)id);
        printf("Next Step: Fetch GET /data/%llu.json\n", (unsigned long long)id);
    } else {
        printf("Intent not recognized.\n");
    }
    return 0;
}
