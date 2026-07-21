param(
    [string]$OutputFile = "i5_benchmark_results.json"
)

Write-Host "====================================================="
Write-Host " LEO AI HARDWARE BENCHMARK (INTEL CORE i5-12450H) "
Write-Host "====================================================="
Write-Host "System: 16 GB RAM / 512 GB SSD"
Write-Host "GPU: Integrated / CPU-Only Mode"
Write-Host ""
Write-Host "Running LEO Benchmarks (Speculative Decoding, BitNet, KV Cache)..."
python core_ai/benchmarker.py --output $OutputFile

Write-Host "====================================================="
Write-Host "Benchmark complete!"
Write-Host "Results saved to: $OutputFile"
Write-Host "====================================================="
