"""
scripts/build_native_keystone.py
================================
Project LEO - Native C++ AVX2 Keystone Kernel Compilation Script.

Cross-compiler automated detection:
  - MSVC (cl.exe): cl /O2 /arch:AVX2 /EHsc /LD backend/hardware/keystone_engine.cpp /Fe:backend/hardware/keystone_engine.dll
  - GCC (g++):     g++ -O3 -mavx2 -mfma -mpopcnt -shared -fPIC backend/hardware/keystone_engine.cpp -o backend/hardware/keystone_engine.dll (.so)
  - Clang (clang++): clang++ -O3 -mavx2 -mfma -mpopcnt -shared -fPIC backend/hardware/keystone_engine.cpp -o backend/hardware/keystone_engine.dll (.so)

Tests loading via ctypes.CDLL and validates symbol resolution.
"""

from __future__ import annotations

import ctypes
import os
import platform
import shutil
import subprocess
import sys
import time
from typing import Dict, Any, Optional, Tuple


def find_cpp_compiler() -> Tuple[Optional[str], Optional[str]]:
    """
    Detects available C++ compiler.
    Returns (compiler_type, executable_path) where compiler_type is 'msvc', 'gcc', or 'clang'.
    """
    # 0. Check provisioned local compiler
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_gpp = os.path.join(workspace_root, "backend", "hardware", ".compiler", "w64devkit", "bin", "g++.exe")
    if os.path.exists(local_gpp):
        return "gcc", local_gpp

    # 1. Check system PATH
    for comp, c_type in [("cl.exe", "msvc"), ("cl", "msvc"), ("g++", "gcc"), ("clang++", "clang")]:
        p = shutil.which(comp)
        if p and not p.lower().endswith(".cpl"):
            return c_type, p

    # 2. Check standard Windows installations if on Windows
    if platform.system() == "Windows":
        vswhere = os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe")
        if os.path.exists(vswhere):
            try:
                out = subprocess.check_output([
                    vswhere, "-latest", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                    "-property", "installationPath"
                ], text=True).strip()
                if out and os.path.exists(out):
                    vc_dir = os.path.join(out, "VC", "Tools", "MSVC")
                    if os.path.exists(vc_dir):
                        versions = sorted(os.listdir(vc_dir), reverse=True)
                        for v in versions:
                            cl_path = os.path.join(vc_dir, v, "bin", "Hostx64", "x64", "cl.exe")
                            if os.path.exists(cl_path):
                                return "msvc", cl_path
            except Exception:
                pass

        llvm_bin = r"C:\Program Files\LLVM\bin\clang++.exe"
        if os.path.exists(llvm_bin):
            return "clang", llvm_bin

        mingw_bins = [
            r"C:\msys64\ucrt64\bin\g++.exe",
            r"C:\msys64\mingw64\bin\g++.exe",
            r"C:\MinGW\bin\g++.exe",
        ]
        for mb in mingw_bins:
            if os.path.exists(mb):
                return "gcc", mb

    return None, None


def build_keystone_library(force: bool = False) -> Dict[str, Any]:
    """
    Builds backend/hardware/keystone_engine.cpp into a shared library.
    """
    system = platform.system()
    ext = ".dll" if system == "Windows" else (".dylib" if system == "Darwin" else ".so")
    
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_file = os.path.join(workspace_root, "backend", "hardware", "keystone_engine.cpp")
    out_dir = os.path.join(workspace_root, "backend", "hardware")
    out_binary = os.path.join(out_dir, f"keystone_engine{ext}")

    if not os.path.exists(src_file):
        return {
            "success": False,
            "binary_path": None,
            "compiler": None,
            "error": f"Source file not found: {src_file}"
        }

    c_type, c_path = find_cpp_compiler()
    if not c_path:
        return {
            "success": False,
            "binary_path": out_binary if os.path.exists(out_binary) else None,
            "compiler": None,
            "error": "No C++ compiler found (cl.exe, g++, or clang++)."
        }

    # Build command based on compiler type
    if c_type == "msvc":
        cmd = [
            c_path,
            "/O2",
            "/arch:AVX2",
            "/EHsc",
            "/LD",
            src_file,
            f"/Fe:{out_binary}",
            f"/Fo:{os.path.join(out_dir, 'keystone_engine.obj')}"
        ]
    elif c_type in ("gcc", "clang"):
        cmd = [
            c_path,
            "-O3",
            "-mavx2",
            "-mfma",
            "-mpopcnt",
            "-shared",
            "-fPIC",
            src_file,
            "-o", out_binary
        ]
        if system != "Windows":
            cmd.append("-lpthread")
    else:
        return {
            "success": False,
            "binary_path": None,
            "compiler": c_type,
            "error": f"Unsupported compiler type: {c_type}"
        }

    print(f"Executing: {' '.join(cmd)}")
    t0 = time.perf_counter()
    env = os.environ.copy()
    c_dir = os.path.dirname(os.path.abspath(c_path))
    env["PATH"] = c_dir + os.pathsep + env.get("PATH", "")
    try:
        proc = subprocess.run(cmd, cwd=out_dir, env=env, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return {
                "success": False,
                "binary_path": None,
                "compiler": c_type,
                "compiler_path": c_path,
                "error": f"Compilation failed: {proc.stderr}\n{proc.stdout}"
            }
    except Exception as e:
        return {
            "success": False,
            "binary_path": None,
            "compiler": c_type,
            "compiler_path": c_path,
            "error": str(e)
        }

    # Verify loading and execute live self-tests
    try:
        import numpy as np

        lib = ctypes.CDLL(out_binary)
        # Check required symbols
        assert hasattr(lib, "leo_evaluate_entropy_avx2"), "Missing symbol: leo_evaluate_entropy_avx2"
        assert hasattr(lib, "leo_execute_vsa_xor_popcnt_avx2"), "Missing symbol: leo_execute_vsa_xor_popcnt_avx2"
        assert hasattr(lib, "leo_tmac_ternary_gemv_avx2"), "Missing symbol: leo_tmac_ternary_gemv_avx2"

        # Configure ctypes signatures
        lib.leo_evaluate_entropy_avx2.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t]
        lib.leo_evaluate_entropy_avx2.restype = ctypes.c_float

        lib.leo_execute_vsa_xor_popcnt_avx2.argtypes = [
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
        ]
        lib.leo_execute_vsa_xor_popcnt_avx2.restype = None

        lib.leo_tmac_ternary_gemv_avx2.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        lib.leo_tmac_ternary_gemv_avx2.restype = None

        # 1. Live Self-Test: VSA XOR Popcount
        v1 = np.array([0xAAAAAAAAAAAAAAAA, 0x5555555555555555], dtype=np.uint64)
        v2 = np.array([0x5555555555555555, 0xAAAAAAAAAAAAAAAA], dtype=np.uint64)
        accum = ctypes.c_uint32(0)
        lib.leo_execute_vsa_xor_popcnt_avx2(
            v1.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
            v2.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
            ctypes.byref(accum),
            128
        )
        assert accum.value == 128, f"VSA self-test mismatch: expected 128, got {accum.value}"

        # 2. Live Self-Test: Ternary GEMV
        rng = np.random.default_rng(42)
        M_test, K_test = 32, 64
        # Random ternary weights in {-1, 0, 1}
        W_tern = rng.choice([-1, 0, 1], size=(M_test, K_test)).astype(np.int8)
        row_scales = rng.uniform(0.5, 2.0, size=M_test).astype(np.float32)
        x_vec = rng.standard_normal(K_test).astype(np.float32)

        # Pack 4 weights per byte (code = weight + 1 in {0, 1, 2})
        code_w = (W_tern + 1).astype(np.uint8)
        b0 = code_w[:, 0::4]
        b1 = code_w[:, 1::4] << 2
        b2 = code_w[:, 2::4] << 4
        b3 = code_w[:, 3::4] << 6
        packed_bytes = np.ascontiguousarray(b0 | b1 | b2 | b3, dtype=np.uint8)

        out_c = np.zeros(M_test, dtype=np.float32)
        lib.leo_tmac_ternary_gemv_avx2(
            packed_bytes.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            row_scales.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            x_vec.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            out_c.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            M_test,
            K_test
        )
        out_ref = (W_tern.astype(np.float32) @ x_vec) * row_scales
        np.testing.assert_allclose(out_c, out_ref, rtol=1e-5, atol=1e-5)

        # 3. Live Self-Test: Shannon Entropy
        ent = lib.leo_evaluate_entropy_avx2(
            x_vec.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            K_test
        )
        assert 0.0 <= ent <= 1.0

        return {
            "success": True,
            "binary_path": out_binary,
            "compiler": c_type,
            "compiler_path": c_path,
            "symbols_verified": True,
            "self_test_passed": True
        }
    except Exception as e:
        return {
            "success": False,
            "binary_path": out_binary,
            "compiler": c_type,
            "compiler_path": c_path,
            "error": f"Library verification failed: {e}"
        }


if __name__ == "__main__":
    res = build_keystone_library()
    print("Build result:", res)
    if not res.get("success"):
        print("Note: Native keystone build failed:", res.get("error"))
        sys.exit(1)
    else:
        print("[PASS] Native keystone compiled, loaded, and verified successfully.")

