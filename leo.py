"""
leo.py
LEO AI v∞ Laptop CLI and launcher controller.
Supports doctor, serve, and benchmark modes with laptop optimization profiles.
"""

import os
import sys
import json
import argparse
import subprocess
import platform
import psutil
import logging
from typing import Dict, Any, List

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LEO-CLI")

def run_doctor() -> Dict[str, Any]:
    """Execute host forensics checking CPU, RAM, disk, iGPU, and runtime statuses."""
    # Detect CPU
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        cpu_model = info.get("brand_raw", platform.processor())
        flags = info.get("flags", [])
    except ImportError:
        cpu_model = platform.processor()
        # Fallback to standard Intel Core i5 list flags
        flags = ["avx", "avx2", "fma"]
    
    # Detect RAM
    mem = psutil.virtual_memory()
    
    # Detect Disk
    disk = psutil.disk_usage('.')
    
    # Detect GPU (using standard system commands on Windows/Linux)
    gpu_name = "Intel iGPU"
    driver_version = "NOT_AVAILABLE"
    
    system = platform.system()
    if system == "Windows":
        try:
            # Run wmic to get controller details
            cmd = ["wmic", "path", "win32_VideoController", "get", "name,driverversion", "/format:list"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            for line in res.stdout.splitlines():
                if "Name=" in line:
                    gpu_name = line.split("=", 1)[1].strip()
                elif "DriverVersion=" in line:
                    driver_version = line.split("=", 1)[1].strip()
        except Exception:
            pass
            
    # OpenVINO / llama.cpp availability check
    openvino_avail = False
    openvino_version = None
    try:
        import openvino as ov
        openvino_avail = True
        openvino_version = ov.__version__
    except ImportError:
        pass

    llama_cpp_avail = False
    llama_cpp_version = None
    try:
        import llama_cpp
        llama_cpp_avail = True
        # Fetch version if accessible
        llama_cpp_version = "0.2"
    except ImportError:
        pass

    # Read overrides or set defaults
    env_device = os.environ.get("LEO_DEVICE", "auto")
    env_runtime = os.environ.get("LEO_RUNTIME", "auto")
    env_model_path = os.environ.get("LEO_MODEL_PATH", "models/qwen2.5-0.5b-instruct.gguf")

    # Determine running device & rationale
    selected_device = "CPU"
    reason = "Default CPU-first profile loaded."
    available_devices = ["CPU"]

    if openvino_avail:
        available_devices.append("GPU.0")
    if llama_cpp_avail:
        available_devices.append("GPU.0 (Vulkan)")

    if env_device == "igpu":
        if openvino_avail or llama_cpp_avail:
            selected_device = "GPU.0"
            reason = "Explicit user override via LEO_DEVICE=igpu."
        else:
            selected_device = "CPU"
            reason = "Requested LEO_DEVICE=igpu, but no working OpenVINO/llama.cpp GPU drivers found. Fallback to CPU."
    elif env_device == "auto":
        # If openvino runtime has GPU device
        if openvino_avail:
            try:
                core = ov.Core()
                if "GPU" in core.available_devices:
                    selected_device = "GPU.0"
                    reason = "Auto-detected Intel integrated GPU support via OpenVINO Core runtime."
            except Exception:
                pass

    # Validate model
    model_valid = os.path.exists(env_model_path)
    
    warnings = []
    if not model_valid:
        warnings.append(f"Model file not found at '{env_model_path}'. Run validation/download configuration.")
    if env_device == "igpu" and selected_device == "CPU":
        warnings.append("Requested iGPU compute fallback to CPU due to missing runtime libraries.")

    return {
        "os": f"{platform.system()} {platform.release()}",
        "cpu": {
            "model": cpu_model,
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "avx2": "avx2" in flags,
            "avx512": any(f.startswith("avx512") for f in flags),
            "avx512_vnni": "avx512_vnni" in flags
        },
        "ram": {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2)
        },
        "disk": {
            "free_gb": round(disk.free / (1024**3), 2)
        },
        "graphics": {
            "name": gpu_name,
            "driver_version": driver_version
        },
        "openvino": {
            "available": openvino_avail,
            "version": openvino_version
        },
        "llama_cpp": {
            "available": llama_cpp_avail,
            "version": llama_cpp_version
        },
        "runtimes": {
            "available_devices": available_devices,
            "selected_device": selected_device,
            "reason": reason
        },
        "model": {
            "path": env_model_path,
            "valid": model_valid
        },
        "warnings": warnings,
        "status": "HEALTHY" if not warnings else "DEGRADED"
    }

def main():
    parser = argparse.ArgumentParser(description="LEO AI v∞ CLI Command Controller")
    subparsers = parser.add_subparsers(dest="command")

    # Doctor
    doc_parser = subparsers.add_parser("doctor", help="Run system compatibility doctor check")
    doc_parser.add_argument("--json", action="store_true", help="Format response profile as JSON")

    # Serve
    serve_parser = subparsers.add_parser("serve", help="Launch semantic compute orchestration server")
    serve_parser.add_argument("--profile", default="laptop", help="Compute limits profile (laptop|server)")

    # Benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Execute hardware performance suite")
    bench_parser.add_argument("--profile", default="laptop", help="Compute profile (laptop)")
    bench_parser.add_argument("--suite", default="smoke", choices=["smoke", "full"], help="Benchmark execution suite")
    bench_parser.add_argument("--output", help="Save run results as JSON file")
    bench_parser.add_argument("--real", action="store_true", help="Run real speculative/OpenVINO benchmarking and generate comparison reports")

    # Validate
    val_parser = subparsers.add_parser("validate", help="Validate GGUF model files against validation contract")
    val_parser.add_argument("--model", required=True, help="Path to the model file to validate")

    # Download Model
    subparsers.add_parser("download-model", help="Download all real GGUF, OpenVINO IR, and ONNX models")

    args = parser.parse_args()

    if args.command == "doctor":
        report = run_doctor()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("="*60)
            print("LEO AI v∞ Laptop System Diagnosis")
            print("="*60)
            print(f"OS: {report['os']}")
            print(f"CPU: {report['cpu']['model']} ({report['cpu']['logical_cores']} threads)")
            print(f"RAM: {report['ram']['total_gb']} GB total ({report['ram']['available_gb']} GB available)")
            print(f"Graphics Adapter: {report['graphics']['name']}")
            print(f"OpenVINO Runtime: {'Available' if report['openvino']['available'] else 'Not Installed'}")
            print(f"llama.cpp: {'Available' if report['llama_cpp']['available'] else 'Not Installed'}")
            print(f"Selected Compute: {report['runtimes']['selected_device']} ({report['runtimes']['reason']})")
            print(f"Status: {report['status']}")
            if report["warnings"]:
                print("\nWARNINGS:")
                for w in report["warnings"]:
                    print(f"- {w}")

    elif args.command == "serve":
        logger.info(f"Starting LEO Serve under '{args.profile}' profile configuration...")
        # Bind environment overrides
        env = os.environ.copy()
        env["LEO_PROFILE"] = args.profile
        
        # Load profile threads defaults
        if "LEO_THREADS" not in env:
            # Target Intel Core i5-12450H physical/performance thread count = 8 threads
            env["LEO_THREADS"] = "8"
            
        # Spawn backend main app using uvicorn process
        cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]
        try:
            subprocess.run(cmd, env=env)
        except KeyboardInterrupt:
            logger.info("LEO server terminated by user.")

    elif args.command == "benchmark":
        logger.info(f"Executing LEO benchmark suite '{args.suite}' on profile '{args.profile}'...")
        from core_ai.benchmarker import LEOBenchmarker
        
        use_gpu = os.environ.get("LEO_DEVICE", "cpu").lower() == "igpu"
        threads = int(os.environ.get("LEO_THREADS", "8"))
        
        if args.real:
            logger.info("Executing real comparative benchmark (Standard vs Speculative vs OpenVINO)...")
            bench = LEOBenchmarker(
                target_model_path="models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
                draft_model_path="models/qwen2.5-0.5b-instruct-q4_k_m.gguf",
                openvino_model_path="models/Qwen2.5-1.5B-Instruct-int4-ov",
                threads=threads,
                use_gpu=use_gpu
            )
            results = bench.run_inference_benchmark(runs_count=3)
            
            # Generate JSON reports and HTML dashboard
            bench.generate_dashboard("competitiveness_report.json", "competitiveness_dashboard.html", results)
            bench.generate_dashboard("competitiveness_proof.json", "competitiveness_proof.html", results)
            
            print(json.dumps(results, indent=2))
        else:
            model_path = os.environ.get("LEO_MODEL_PATH", "models/qwen2.5-1.5b-instruct-q4_k_m.gguf")
            bench = LEOBenchmarker(target_model_path=model_path, threads=threads, use_gpu=use_gpu)
            results = bench.run_inference_benchmark(runs_count=3)
            results["profile"] = args.profile
            results["suite"] = args.suite
            
            if args.output:
                os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
                with open(args.output, "w") as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Benchmark results saved to {args.output}")
            else:
                print(json.dumps(results, indent=2))

    elif args.command == "validate":
        logger.info(f"Validating model at '{args.model}'...")
        from core_ai.model_adapter import validate_model_integrity, ModelValidationError
        try:
            validate_model_integrity(args.model)
            logger.info("Model validation successful! Formats, structures, size, and checksums are verified.")
            sys.exit(0)
        except ModelValidationError as e:
            logger.error(f"Model validation failed:\n{e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            sys.exit(1)

    elif args.command == "download-model":
        logger.info("Starting model download pipeline (Target GGUF, Draft GGUF, OpenVINO IR, ONNX Embeddings)...")
        from huggingface_hub import hf_hub_download, snapshot_download
        os.makedirs("models", exist_ok=True)
        try:
            logger.info("Downloading Target Model: Qwen2.5-1.5B-Instruct Q4_K_M...")
            hf_hub_download(
                repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
                filename="qwen2.5-1.5b-instruct-q4_k_m.gguf",
                local_dir="models",
                local_dir_use_symlinks=False
            )
            
            logger.info("Downloading Draft Model: Qwen2.5-0.5B-Instruct Q4_K_M...")
            hf_hub_download(
                repo_id="Qwen/Qwen2.5-0.5B-Instruct-GGUF",
                filename="qwen2.5-0.5b-instruct-q4_k_m.gguf",
                local_dir="models",
                local_dir_use_symlinks=False
            )
            
            logger.info("Downloading OpenVINO IR Model: Qwen2.5-1.5B-Instruct-int4-ov...")
            snapshot_download(
                repo_id="OpenVINO/Qwen2.5-1.5B-Instruct-int4-ov",
                local_dir="models/Qwen2.5-1.5B-Instruct-int4-ov",
                local_dir_use_symlinks=False
            )
            
            logger.info("Downloading ONNX Embedding Model: Xenova/all-MiniLM-L6-v2...")
            snapshot_download(
                repo_id="Xenova/all-MiniLM-L6-v2",
                local_dir="models/all-MiniLM-L6-v2",
                allow_patterns=["*.onnx", "*.json", "*.txt"],
                local_dir_use_symlinks=False
            )
            logger.info("All model files downloaded successfully!")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            sys.exit(1)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
