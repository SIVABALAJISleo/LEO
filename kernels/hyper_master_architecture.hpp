/**
 * ============================================================================
 * PROJECT LEO (HYPER) - MASTER BYPASS ARCHITECTURE SPECIFICATION
 * ============================================================================
 * Hardware Envelope: Intel Core i5-12450H (4 P-cores, 4 E-cores, AVX2)
 *                    16 GB RAM (UMA Ring Bus), Intel UHD Graphics (48 EUs), Windows 11.
 * 
 * Prime Directive: Achieve 100% Contract & Application Parity on structured workloads.
 *                  Do not make this hardware compute dense floating-point math faster.
 *                  Mathematically eliminate the need for dense floating-point math entirely.
 * 
 * The Wormhole Philosophy:
 *  1. Do not compute what you can look up.
 *  2. Do not execute floating-point matrices when you can XOR hyperdimensional bits.
 *  3. Do not transfer data across a PCIe bus when you can share unified memory pointers.
 *  4. Do not traverse a computational graph if the topological destination is already known.
 * ============================================================================
 */

#pragma once

#ifndef HYPER_MASTER_ARCHITECTURE_HPP
#define HYPER_MASTER_ARCHITECTURE_HPP

#include "vsa/hyper_vsa_10k_engine.hpp"
#include "usm/hyper_usm_svm_runtime.hpp"
#include "pruning/hyper_homotopic_prover.hpp"
#include "memoization/hyper_l3_memoization.hpp"

namespace hyper::wormhole {

/**
 * Top-Level Wormhole Execution Context
 */
struct WormholeContext {
    // Pillar 1: VSA 10K Engine State
    bool vsa_enabled = true;
    bool pcores_pinned = false;

    // Pillar 2: Zero-Copy USM State
    bool usm_svm_enabled = true;
    size_t usm_allocated_bytes = 0;

    // Pillar 3: Homotopic Path Contraction State
    bool homotopic_pruning_enabled = true;
    pruning::PruningReport last_pruning_report{};

    // Pillar 4: Semantic Memoization & Entropy Fallback State
    bool memoization_enabled = true;
    memoization::MemoizationTelemetry memo_telemetry{};
};

/**
 * Initializes the entire Wormhole Master Engine across all 4 pillars.
 */
inline int initialize_wormhole_system(WormholeContext& ctx) {
    // 1. Pin VSA execution to Golden Cove P-cores (logical cores 0..3)
    if (vsa::vsa_10k_pin_pcores() == 0) {
        ctx.pcores_pinned = true;
    }

    // 2. Initialize Heterogeneous USM / SVM runtime
    if (usm::usm_svm_init_runtime() == 0) {
        ctx.usm_svm_enabled = true;
    }

    // 3. Initialize 8MB L3-budgeted memoization table
    if (memoization::memo_init_table() == 0) {
        ctx.memoization_enabled = true;
    }

    return 0;
}

/**
 * Shuts down all four pillars and releases resources cleanly.
 */
inline void shutdown_wormhole_system(WormholeContext& ctx) {
    memoization::memo_shutdown_table();
    usm::usm_svm_shutdown_runtime();
    ctx.usm_allocated_bytes = 0;
}

} // namespace hyper::wormhole

#endif // HYPER_MASTER_ARCHITECTURE_HPP
