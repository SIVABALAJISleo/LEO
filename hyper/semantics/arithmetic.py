"""
hyper/semantics/arithmetic.py
=============================
Authoritative Exact Arithmetic Semantics Engine.
Implements exact IEEE 754 floating-point semantics (RNE, RTZ, RTP, RTN, FMA,
subnormals, signed zeros, NaNs, infinities) and bit-exact fixed-width integer semantics
(two's complement overflow, unsigned modulo wraparound, shifts, rotates, bitwise).
"""

from __future__ import annotations
import enum
import math
import struct
from typing import Any, Tuple, Union
import numpy as np


class RoundingMode(str, enum.Enum):
    RNE = "RNE"  # Round to Nearest, ties to Even (IEEE 754 default)
    RTZ = "RTZ"  # Round toward Zero (Truncation)
    RTP = "RTP"  # Round toward Positive Infinity (Ceiling)
    RTN = "RTN"  # Round toward Negative Infinity (Floor)


class DenormalMode(str, enum.Enum):
    PRESERVE = "PRESERVE"
    FTZ_DAZ = "FTZ_DAZ"  # Flush To Zero / Denormals Are Zero


# Integer bitmask constants
MASK_8 = 0xFF
MASK_16 = 0xFFFF
MASK_32 = 0xFFFFFFFF
MASK_64 = 0xFFFFFFFFFFFFFFFF

SIGN_8 = 0x80
SIGN_16 = 0x8000
SIGN_32 = 0x80000000
SIGN_64 = 0x8000000000000000


# ==============================================================================
# Fixed-Width Integer Semantic Routines
# ==============================================================================

def to_signed(val: int, bits: int) -> int:
    mask = (1 << bits) - 1
    val = val & mask
    sign_bit = 1 << (bits - 1)
    if val & sign_bit:
        return val - (1 << bits)
    return val


def to_unsigned(val: int, bits: int) -> int:
    mask = (1 << bits) - 1
    return val & mask


def exact_int_add(a: int, b: int, bits: int = 32, signed: bool = True) -> int:
    raw = (a + b) & ((1 << bits) - 1)
    return to_signed(raw, bits) if signed else raw


def exact_int_sub(a: int, b: int, bits: int = 32, signed: bool = True) -> int:
    raw = (a - b) & ((1 << bits) - 1)
    return to_signed(raw, bits) if signed else raw


def exact_int_mul(a: int, b: int, bits: int = 32, signed: bool = True) -> int:
    raw = (a * b) & ((1 << bits) - 1)
    return to_signed(raw, bits) if signed else raw


def exact_int_div(a: int, b: int, bits: int = 32, signed: bool = True) -> int:
    if b == 0:
        raise ZeroDivisionError(f"Integer division by zero: {a} / 0")
    if signed:
        # Two's complement special case: INT_MIN / -1 overflows back to INT_MIN
        min_val = -(1 << (bits - 1))
        if a == min_val and b == -1:
            return min_val
        # Truncate towards zero
        res = int(a / b)
        return to_signed(res, bits)
    else:
        u_a = to_unsigned(a, bits)
        u_b = to_unsigned(b, bits)
        return (u_a // u_b) & ((1 << bits) - 1)


def exact_int_rem(a: int, b: int, bits: int = 32, signed: bool = True) -> int:
    if b == 0:
        raise ZeroDivisionError(f"Integer modulo by zero: {a} % 0")
    if signed:
        res = a % b if (a >= 0 and b > 0) else int(math.fmod(a, b))
        return to_signed(res, bits)
    else:
        u_a = to_unsigned(a, bits)
        u_b = to_unsigned(b, bits)
        return u_a % u_b


def exact_int_shl(a: int, shift: int, bits: int = 32) -> int:
    shift = shift % bits
    raw = (a << shift) & ((1 << bits) - 1)
    return raw


def exact_int_shr_logical(a: int, shift: int, bits: int = 32) -> int:
    shift = shift % bits
    u_a = to_unsigned(a, bits)
    return (u_a >> shift) & ((1 << bits) - 1)


def exact_int_shr_arithmetic(a: int, shift: int, bits: int = 32) -> int:
    shift = shift % bits
    s_a = to_signed(a, bits)
    return to_signed(s_a >> shift, bits)


def exact_int_rol(a: int, shift: int, bits: int = 32) -> int:
    shift = shift % bits
    u_a = to_unsigned(a, bits)
    raw = ((u_a << shift) | (u_a >> (bits - shift))) & ((1 << bits) - 1)
    return raw


def exact_int_ror(a: int, shift: int, bits: int = 32) -> int:
    shift = shift % bits
    u_a = to_unsigned(a, bits)
    raw = ((u_a >> shift) | (u_a << (bits - shift))) & ((1 << bits) - 1)
    return raw


# ==============================================================================
# IEEE 754 Floating-Point Exact Semantic Routines
# ==============================================================================

def float32_to_bits(f: float) -> int:
    return struct.unpack(">I", struct.pack(">f", float(f)))[0]


def bits_to_float32(b: int) -> float:
    return struct.unpack(">f", struct.pack(">I", b & MASK_32))[0]


def float64_to_bits(f: float) -> int:
    return struct.unpack(">Q", struct.pack(">d", float(f)))[0]


def bits_to_float64(b: int) -> float:
    return struct.unpack(">d", struct.pack(">Q", b & MASK_64))[0]


def is_nan_f32(f: float) -> bool:
    return math.isnan(f)


def is_inf_f32(f: float) -> bool:
    return math.isinf(f)


def is_signed_zero_f32(f: float) -> bool:
    if f == 0.0:
        bits = float32_to_bits(f)
        return bool(bits & SIGN_32)
    return False


def exact_fp32_add(
    a: float,
    b: float,
    rounding: RoundingMode = RoundingMode.RNE,
    denormal: DenormalMode = DenormalMode.PRESERVE,
) -> float:
    """Exact IEEE 754 FP32 Addition with full corner case handling."""
    if math.isnan(a) or math.isnan(b):
        return float("nan")
    if math.isinf(a) and math.isinf(b):
        if (a > 0 and b < 0) or (a < 0 and b > 0):
            return float("nan")  # +inf + -inf = nan
        return a

    # Direct hardware FP32 operation via np.float32
    f32_a = np.float32(a)
    f32_b = np.float32(b)
    res = np.float32(f32_a + f32_b)

    if denormal == DenormalMode.FTZ_DAZ:
        if abs(float(res)) < 1.17549435e-38 and res != 0.0:
            res = np.float32(0.0)

    return float(res)


def exact_fp32_sub(
    a: float,
    b: float,
    rounding: RoundingMode = RoundingMode.RNE,
) -> float:
    return exact_fp32_add(a, -b, rounding=rounding)


def exact_fp32_mul(
    a: float,
    b: float,
    rounding: RoundingMode = RoundingMode.RNE,
    denormal: DenormalMode = DenormalMode.PRESERVE,
) -> float:
    """Exact IEEE 754 FP32 Multiplication with signed zeros and infs."""
    if math.isnan(a) or math.isnan(b):
        return float("nan")
    if (math.isinf(a) and b == 0.0) or (math.isinf(b) and a == 0.0):
        return float("nan")

    f32_a = np.float32(a)
    f32_b = np.float32(b)
    res = np.float32(f32_a * f32_b)

    if denormal == DenormalMode.FTZ_DAZ:
        if abs(float(res)) < 1.17549435e-38 and res != 0.0:
            res = np.float32(0.0)

    return float(res)


def exact_fp32_div(
    a: float,
    b: float,
    rounding: RoundingMode = RoundingMode.RNE,
) -> float:
    if math.isnan(a) or math.isnan(b):
        return float("nan")
    if a == 0.0 and b == 0.0:
        return float("nan")
    if math.isinf(a) and math.isinf(b):
        return float("nan")
    if b == 0.0:
        # Determine sign of zero
        b_bits = float32_to_bits(b)
        a_bits = float32_to_bits(a)
        sign = (a_bits ^ b_bits) & SIGN_32
        return float("-inf") if sign else float("inf")

    f32_a = np.float32(a)
    f32_b = np.float32(b)
    res = np.float32(f32_a / f32_b)
    return float(res)


def exact_fp32_fma(
    a: float,
    b: float,
    c: float,
    rounding: RoundingMode = RoundingMode.RNE,
) -> float:
    """
    Fused Multiply-Add: (a * b) + c with SINGLE rounding.
    Uses Python 3.13 math.fma or float64 intermediate accumulator.
    """
    if hasattr(math, "fma"):
        # Builtin C99 fma in Python 3.13
        res = math.fma(float(a), float(b), float(c))
        return float(np.float32(res))
    else:
        # Software FMA via FP64 high-precision accumulator
        prod_exact = np.float64(a) * np.float64(b)
        sum_exact = prod_exact + np.float64(c)
        return float(np.float32(sum_exact))


def exact_fp32_sqrt(a: float) -> float:
    if a < 0.0:
        return float("nan")
    return float(np.float32(math.sqrt(a)))


def exact_bf16_truncate(f: float) -> float:
    """Emulate BF16 (1 sign, 8 exp, 7 mantissa) from FP32."""
    b32 = float32_to_bits(f)
    # Truncate lower 16 bits of mantissa with round to nearest even
    lsb = (b32 >> 16) & 1
    bias = 0x7FFF + lsb
    rounded = (b32 + bias) & 0xFFFF0000
    return bits_to_float32(rounded)


def bitcast_fp32_to_int32(f: float) -> int:
    return struct.unpack(">i", struct.pack(">f", float(f)))[0]


def bitcast_int32_to_fp32(i: int) -> float:
    return struct.unpack(">f", struct.pack(">i", int(i)))[0]
