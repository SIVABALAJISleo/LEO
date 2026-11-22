#!/usr/bin/env python3
"""
backend/native/build_native_kernels.py
==============================================================================
Project LEO / HYPER-Omega: Native C99 AVX2 Kernel Compiler and Auto-Loader.
Target Hardware: Intel Core i5-12450H (AVX2 + FMA).

Compiles and validates:
  1. avx2_bitslice_lut_kernels.c -> avx2_bitslice_lut_kernels.dll
  2. leo_async_direct_io.c       -> leo_async_direct_io.dll
  3. leo_rans_codec.c            -> leo_rans_codec.dll
==============================================================================
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def find_c_compiler():
    # 1. Check embedded w64devkit MinGW gcc
    repo_root = Path(__file__).resolve().parent.parent.parent
    embedded_gcc = repo_root / "backend" / "hardware" / ".compiler" / "w64devkit" / "bin" / "gcc.exe"
    if embedded_gcc.exists():
        bin_dir = str(embedded_gcc.parent)
        current_path = os.environ.get("PATH", "")
        if bin_dir not in current_path:
            os.environ["PATH"] = bin_dir + os.pathsep + current_path
        return str(embedded_gcc), "gcc"

    # 2. Check system gcc
    sys_gcc = shutil.which("gcc")
    if sys_gcc:
        return sys_gcc, "gcc"

    # 3. Check clang
    sys_clang = shutil.which("clang")
    if sys_clang:
        return sys_clang, "clang"

    # 4. Check cl.exe (MSVC)
    sys_cl = shutil.which("cl")
    if sys_cl:
        return sys_cl, "msvc"

    return None, None


def compile_shared_library(src_file: Path, out_file: Path) -> bool:
    compiler, c_type = find_c_compiler()
    if not compiler:
        print(f"[WARN] No C compiler found. Skipping native compilation for {src_file.name}")
        return False

    out_file.parent.mkdir(parents=True, exist_ok=True)

    if c_type in ("gcc", "clang"):
        cmd = [
            compiler,
            "-O3",
            "-mavx2",
            "-shared",
            "-fPIC",
            str(src_file),
            "-o",
            str(out_file),
        ]
    elif c_type == "msvc":
        cmd = [
            compiler,
            "/O2",
            "/arch:AVX2",
            "/LD",
            str(src_file),
            f"/Fe:{out_file}",
        ]
    else:
        return False

    env = os.environ.copy()
    compiler_bin = str(Path(compiler).parent)
    if compiler_bin not in env.get("PATH", ""):
        env["PATH"] = compiler_bin + os.pathsep + env.get("PATH", "")

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
        if res.returncode == 0:
            print(f"[OK] Compiled {src_file.name} -> {out_file.name}")
            return True
        else:
            print(f"[ERR] Failed compiling {src_file.name}: {res.stderr}")
            return False
    except Exception as e:
        print(f"[ERR] Exception compiling {src_file.name}: {e}")
        return False


def build_all_native_kernels():
    native_dir = Path(__file__).resolve().parent
    targets = [
        ("avx2_bitslice_lut_kernels.c", "avx2_bitslice_lut_kernels.dll" if sys.platform == "win32" else "avx2_bitslice_lut_kernels.so"),
        ("leo_async_direct_io.c", "leo_async_direct_io.dll" if sys.platform == "win32" else "leo_async_direct_io.so"),
        ("leo_rans_codec.c", "leo_rans_codec.dll" if sys.platform == "win32" else "leo_rans_codec.so"),
    ]

    success_count = 0
    for src_name, out_name in targets:
        src_path = native_dir / src_name
        out_path = native_dir / out_name
        if src_path.exists():
            if compile_shared_library(src_path, out_path):
                success_count += 1

    print(f"\n[INFO] Native kernel compilation complete: {success_count}/{len(targets)} targets built successfully.")
    return success_count == len(targets)


if __name__ == "__main__":
    ok = build_all_native_kernels()
    sys.exit(0 if ok else 1)
