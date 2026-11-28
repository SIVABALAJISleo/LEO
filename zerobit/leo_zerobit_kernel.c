/*
 * leo_zerobit_kernel.c
 *
 * LEO-ZeroBit: Tile-Group-Major Sparse Ternary {-1, 0, +1} VPSHUFB GEMV Engine
 * Target: Consumer x86-64 AVX2 CPUs (Intel Core i5-12450H) + Hybrid OpenCL iGPU
 *
 * Weight layout (16x smaller than FP32, 8x smaller than FP16):
 *   TILE_M = 512 (M must be a multiple of 512; K must be a multiple of 4)
 *   packed_w[tile][g][tm] holds 4 ternary weights for row (tile*512 + tm)
 *   and input columns (4g, 4g+1, 4g+2, 4g+3):
 *     low  nibble = (w0 + 1) + 3*(w1 + 1)   in [0..8]
 *     high nibble = (w2 + 1) + 3*(w3 + 1)   in [0..8]
 *
 * Guarantees:
 *   - ZERO hardware multiplier instructions in the hot inner loop
 *   - ZERO strided reads when skipping inactive input groups
 *   - ZERO integer overflow for arbitrary int16 inputs/deltas (exact chunk split)
 *   - BIT-EXACT (0 integer error) in Dense, Sparse, and Persistent-Membrane Delta modes
 */

#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#ifdef __AVX2__
#include <immintrin.h>
#endif

#ifdef _WIN32
#define ZB_API __declspec(dllexport)
#else
#define ZB_API
#endif

#define LEO_TILE_M 512

typedef struct {
    int32_t group_idx;
    uint8_t lo_active;
    uint8_t hi_active;
    int8_t  lut_lo[16];
    int8_t  lut_hi[16];
} ActiveChunk;

ZB_API int leo_zerobit_is_avx2(void) {
#ifdef __AVX2__
    return 1;
#else
    return 0;
#endif
}

static inline int16_t take_safe_63(int32_t *rem) {
    int32_t v = *rem;
    int16_t c;
    if (v > 63) {
        c = 63;
    } else if (v < -63) {
        c = -63;
    } else {
        c = (int16_t)v;
    }
    *rem = v - (int32_t)c;
    return c;
}

static inline void fill_pair_lut(int16_t a0, int16_t a1, int8_t lut[16]) {
    /* |a0| <= 63 and |a1| <= 63 => |t0*a0 + t1*a1| <= 126 (strictly fits int8) */
    memset(lut, 0, 16);
    int idx = 0;
    for (int t1 = -1; t1 <= 1; ++t1) {
        for (int t0 = -1; t0 <= 1; ++t0) {
            lut[idx++] = (int8_t)(t0 * a0 + t1 * a1);
        }
    }
}

/*
 * Builds a compact list of ONLY active 4-input groups (with exact safe sub-chunks).
 * Inactive groups (x[4g..4g+3] == 0) are completely omitted -> 0 DRAM reads.
 */
static int build_active_chunks(const int16_t *x, int K, ActiveChunk **out_chunks, int *out_active_groups) {
    int groups = K / 4;
    int cap = groups + 64;
    ActiveChunk *chunks = (ActiveChunk *)malloc((size_t)cap * sizeof(ActiveChunk));
    if (!chunks) return -1;

    int n_chunks = 0;
    int active_groups = 0;

    for (int g = 0; g < groups; ++g) {
        int32_t r0 = (int32_t)x[4 * g + 0];
        int32_t r1 = (int32_t)x[4 * g + 1];
        int32_t r2 = (int32_t)x[4 * g + 2];
        int32_t r3 = (int32_t)x[4 * g + 3];

        if ((r0 | r1 | r2 | r3) == 0) {
            continue;
        }
        active_groups++;

        while ((r0 | r1 | r2 | r3) != 0) {
            if (n_chunks >= cap) {
                cap *= 2;
                ActiveChunk *grown = (ActiveChunk *)realloc(chunks, (size_t)cap * sizeof(ActiveChunk));
                if (!grown) {
                    free(chunks);
                    return -1;
                }
                chunks = grown;
            }
            int16_t c0 = take_safe_63(&r0);
            int16_t c1 = take_safe_63(&r1);
            int16_t c2 = take_safe_63(&r2);
            int16_t c3 = take_safe_63(&r3);

            ActiveChunk *ck = &chunks[n_chunks++];
            ck->group_idx = g;
            ck->lo_active = (uint8_t)((c0 | c1) != 0);
            ck->hi_active = (uint8_t)((c2 | c3) != 0);
            if (ck->lo_active) fill_pair_lut(c0, c1, ck->lut_lo);
            if (ck->hi_active) fill_pair_lut(c2, c3, ck->lut_hi);
        }
    }

    *out_chunks = chunks;
    if (out_active_groups) *out_active_groups = active_groups;
    return n_chunks;
}

#ifdef __AVX2__
static inline void flush_acc16_to_out32_avx2(int16_t *acc16, int32_t *out_tile) {
    const __m256i zero = _mm256_setzero_si256();
    for (int tm = 0; tm < LEO_TILE_M; tm += 16) {
        __m256i a = _mm256_loadu_si256((const __m256i *)(acc16 + tm));
        __m256i o0 = _mm256_loadu_si256((const __m256i *)(out_tile + tm));
        __m256i o1 = _mm256_loadu_si256((const __m256i *)(out_tile + tm + 8));
        o0 = _mm256_add_epi32(o0, _mm256_cvtepi16_epi32(_mm256_castsi256_si128(a)));
        o1 = _mm256_add_epi32(o1, _mm256_cvtepi16_epi32(_mm256_extracti128_si256(a, 1)));
        _mm256_storeu_si256((__m256i *)(out_tile + tm),     o0);
        _mm256_storeu_si256((__m256i *)(out_tile + tm + 8), o1);
        _mm256_storeu_si256((__m256i *)(acc16 + tm),        zero);
    }
}
#endif

/*
 * Computes exact ternary GEMV over tiles [tile_start, tile_end):
 *   if accumulate == 0: out[rows]  = W_tern[rows, :] @ x[:]
 *   if accumulate != 0: out[rows] += W_tern[rows, :] @ x[:]   (Persistent-Membrane Delta)
 *
 * Returns number of active 4-input groups executed (>= 0), or negative error code.
 */
ZB_API int leo_zerobit_gemv_tiles(
    const uint8_t *packed_w,
    const int16_t *x,
    int32_t *out,
    int M,
    int K,
    int tile_start,
    int tile_end,
    int accumulate
) {
    if (!packed_w || !x || !out || M <= 0 || K <= 0 || (M % LEO_TILE_M) != 0 || (K % 4) != 0) {
        return -1;
    }
    int total_tiles = M / LEO_TILE_M;
    if (tile_start < 0 || tile_end > total_tiles || tile_start > tile_end) {
        return -2;
    }
    if (tile_start == tile_end) {
        return 0;
    }

    if (!accumulate) {
        memset(
            out + (size_t)tile_start * LEO_TILE_M,
            0,
            (size_t)(tile_end - tile_start) * LEO_TILE_M * sizeof(int32_t)
        );
    }

    ActiveChunk *chunks = NULL;
    int active_groups = 0;
    int n_chunks = build_active_chunks(x, K, &chunks, &active_groups);
    if (n_chunks < 0) return -3;
    if (n_chunks == 0) {
        free(chunks);
        return 0;
    }

    int groups = K / 4;

#ifdef __AVX2__
    #ifdef _OPENMP
    #pragma omp parallel for schedule(static)
    #endif
    for (int tile = tile_start; tile < tile_end; ++tile) {
        /* 1 KB stack buffer: 100% pinned inside L1d cache per CPU thread */
        int16_t acc16[LEO_TILE_M];
        memset(acc16, 0, sizeof(acc16));

        const __m256i mask_0f = _mm256_set1_epi8(0x0F);
        const uint8_t *tile_w = packed_w + (size_t)tile * (size_t)groups * LEO_TILE_M;
        int32_t *out_tile = out + (size_t)tile * LEO_TILE_M;
        int flush_ctr = 0;

        for (int c = 0; c < n_chunks; ++c) {
            const ActiveChunk *ck = &chunks[c];
            const uint8_t *w_slab = tile_w + (size_t)ck->group_idx * LEO_TILE_M;

            if (ck->lo_active && ck->hi_active) {
                __m256i lut_lo = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)ck->lut_lo));
                __m256i lut_hi = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)ck->lut_hi));
                for (int tm = 0; tm < LEO_TILE_M; tm += 32) {
                    __m256i p = _mm256_loadu_si256((const __m256i *)(w_slab + tm));
                    __m256i s_lo = _mm256_shuffle_epi8(lut_lo, _mm256_and_si256(p, mask_0f));
                    __m256i s_hi = _mm256_shuffle_epi8(lut_hi, _mm256_and_si256(_mm256_srli_epi16(p, 4), mask_0f));

                    __m256i d0 = _mm256_add_epi16(
                        _mm256_cvtepi8_epi16(_mm256_castsi256_si128(s_lo)),
                        _mm256_cvtepi8_epi16(_mm256_castsi256_si128(s_hi))
                    );
                    __m256i d1 = _mm256_add_epi16(
                        _mm256_cvtepi8_epi16(_mm256_extracti128_si256(s_lo, 1)),
                        _mm256_cvtepi8_epi16(_mm256_extracti128_si256(s_hi, 1))
                    );
                    __m256i a0 = _mm256_loadu_si256((const __m256i *)(acc16 + tm));
                    __m256i a1 = _mm256_loadu_si256((const __m256i *)(acc16 + tm + 16));
                    _mm256_storeu_si256((__m256i *)(acc16 + tm),      _mm256_add_epi16(a0, d0));
                    _mm256_storeu_si256((__m256i *)(acc16 + tm + 16), _mm256_add_epi16(a1, d1));
                }
            } else if (ck->lo_active) {
                __m256i lut_lo = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)ck->lut_lo));
                for (int tm = 0; tm < LEO_TILE_M; tm += 32) {
                    __m256i p = _mm256_loadu_si256((const __m256i *)(w_slab + tm));
                    __m256i s_lo = _mm256_shuffle_epi8(lut_lo, _mm256_and_si256(p, mask_0f));
                    __m256i a0 = _mm256_loadu_si256((const __m256i *)(acc16 + tm));
                    __m256i a1 = _mm256_loadu_si256((const __m256i *)(acc16 + tm + 16));
                    _mm256_storeu_si256((__m256i *)(acc16 + tm),      _mm256_add_epi16(a0, _mm256_cvtepi8_epi16(_mm256_castsi256_si128(s_lo))));
                    _mm256_storeu_si256((__m256i *)(acc16 + tm + 16), _mm256_add_epi16(a1, _mm256_cvtepi8_epi16(_mm256_extracti128_si256(s_lo, 1))));
                }
            } else if (ck->hi_active) {
                __m256i lut_hi = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)ck->lut_hi));
                for (int tm = 0; tm < LEO_TILE_M; tm += 32) {
                    __m256i p = _mm256_loadu_si256((const __m256i *)(w_slab + tm));
                    __m256i s_hi = _mm256_shuffle_epi8(lut_hi, _mm256_and_si256(_mm256_srli_epi16(p, 4), mask_0f));
                    __m256i a0 = _mm256_loadu_si256((const __m256i *)(acc16 + tm));
                    __m256i a1 = _mm256_loadu_si256((const __m256i *)(acc16 + tm + 16));
                    _mm256_storeu_si256((__m256i *)(acc16 + tm),      _mm256_add_epi16(a0, _mm256_cvtepi8_epi16(_mm256_castsi256_si128(s_hi))));
                    _mm256_storeu_si256((__m256i *)(acc16 + tm + 16), _mm256_add_epi16(a1, _mm256_cvtepi8_epi16(_mm256_extracti128_si256(s_hi, 1))));
                }
            }

            /* Max |acc16| after 64 chunks = 64 * 252 = 16,128 < 32,767 (zero overflow) */
            if (++flush_ctr == 64) {
                flush_acc16_to_out32_avx2(acc16, out_tile);
                flush_ctr = 0;
            }
        }

        if (flush_ctr > 0) {
            flush_acc16_to_out32_avx2(acc16, out_tile);
        }
    }
#else
    /* Portable exact scalar LUT fallback */
    for (int tile = tile_start; tile < tile_end; ++tile) {
        const uint8_t *tile_w = packed_w + (size_t)tile * (size_t)groups * LEO_TILE_M;
        int32_t *out_tile = out + (size_t)tile * LEO_TILE_M;
        for (int c = 0; c < n_chunks; ++c) {
            const ActiveChunk *ck = &chunks[c];
            const uint8_t *w_slab = tile_w + (size_t)ck->group_idx * LEO_TILE_M;
            for (int tm = 0; tm < LEO_TILE_M; ++tm) {
                uint8_t p = w_slab[tm];
                int32_t delta = 0;
                if (ck->lo_active) delta += (int32_t)ck->lut_lo[p & 0x0F];
                if (ck->hi_active) delta += (int32_t)ck->lut_hi[(p >> 4) & 0x0F];
                out_tile[tm] += delta;
            }
        }
    }
#endif

    free(chunks);
    return active_groups;
}
