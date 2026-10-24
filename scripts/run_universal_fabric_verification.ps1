# ==============================================================================
# scripts/run_universal_fabric_verification.ps1
# LEO / HYPER: Master Universal Replacement Fabric Verification Runner
#
# Target System: Lenovo IdeaPad Slim 3 15IAH8 | Intel Core i5-12450H | Windows 11
# ==============================================================================

[CmdletBinding()]
param (
    [string]$Policy = "AUTO_VERIFIED",
    [int]$Seed = 42,
    [switch]$StrictIgpuCheck = $false,
    [string]$ReportsDir = "reports"
)

$ErrorActionPreference = "Stop"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " LEO / HYPER -- UNIVERSAL REPLACEMENT FABRIC VERIFICATION RUNNER" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Environment & Hardware Probe
Write-Host "[1/6] Probing physical hardware and environment..." -ForegroundColor Yellow
$PythonCmd = "python"

if (-not (Get-Command $PythonCmd -ErrorAction SilentlyContinue)) {
    Write-Error "Python executable not found in PATH."
    exit 1
}

$PyVer = & $PythonCmd -c "import sys; print(sys.version.split()[0])"
$OsName = [System.Environment]::OSVersion.VersionString
$CpuName = (Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name).Trim()
$TotalRamGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)

Write-Host "  OS:           $OsName" -ForegroundColor Gray
Write-Host "  Python:       $PyVer" -ForegroundColor Gray
Write-Host "  Processor:    $CpuName" -ForegroundColor Gray
Write-Host "  Unified RAM:  $TotalRamGB GB" -ForegroundColor Gray

# 2. Dynamic Hardware & Runtime Probe via Python
Write-Host "`n[2/6] Querying Universal Fabric Physical Device Probe..." -ForegroundColor Yellow
$ProbeScript = @"
import json
import hyper_phase_change as hpc

probe = hpc.PhysicalDeviceProbe.run_full_probe()
registry = hpc.CapabilityRegistry()

print(json.dumps({
    'probe': probe.to_dict(),
    'registered_backends': [b.to_dict() for b in registry.list_backends()]
}))
"@

$ProbeJson = & $PythonCmd -c $ProbeScript
$ProbeObj = $ProbeJson | ConvertFrom-Json

Write-Host "  Intel UHD iGPU Available: $($ProbeObj.probe.igpu_available)" -ForegroundColor Gray
Write-Host "  Intel Device Name:        $($ProbeObj.probe.igpu_device_name)" -ForegroundColor Gray
Write-Host "  Intel Probe Verified:     $($ProbeObj.probe.igpu_probe_success)" -ForegroundColor Gray
Write-Host "  Discrete GPU Status:      $($ProbeObj.probe.discrete_gpu_parity_status)" -ForegroundColor Gray
Write-Host "  Registered Backends:      $($ProbeObj.registered_backends.Count)" -ForegroundColor Gray

if ($StrictIgpuCheck -and (-not $ProbeObj.probe.igpu_probe_success)) {
    Write-Error "Strict iGPU check requested, but Intel iGPU probe was not verified."
    exit 2
}

# 3. Canonical 15 Independent Verification
Write-Host "`n[3/6] Running Independent Verification across all 15 Canonical Workloads..." -ForegroundColor Yellow
$VerifyScript = @"
import json
import hyper_phase_change as hpc

report = hpc.PhaseChangeVerifier.run_suite()
cert = hpc.FabricCertificationEngine.evaluate_gates(suite_report=report)

print(json.dumps({
    'report': report.to_dict(),
    'certificate': cert.to_dict()
}))
"@

$VerifyOutput = & $PythonCmd -c $VerifyScript
$VerifyObj = $VerifyOutput | ConvertFrom-Json

Write-Host "  Total Canonical Workloads: $($VerifyObj.report.total_workloads)" -ForegroundColor Gray
Write-Host "  PASSED Workloads:          $($VerifyObj.report.pass_count) / 15" -ForegroundColor Green
Write-Host "  FAILED Workloads:          $($VerifyObj.report.fail_count)" -ForegroundColor $(if ($VerifyObj.report.fail_count -eq 0) { "Gray" } else { "Red" })
Write-Host "  UNKNOWN Workloads:         $($VerifyObj.report.unknown_count)" -ForegroundColor $(if ($VerifyObj.report.unknown_count -eq 0) { "Gray" } else { "Red" })
Write-Host "  BLOCKED Workloads:         $($VerifyObj.report.blocked_count)" -ForegroundColor $(if ($VerifyObj.report.blocked_count -eq 0) { "Gray" } else { "Red" })
Write-Host "  Overall Certification:     $($VerifyObj.certificate.overall_status)" -ForegroundColor Cyan

if ($VerifyObj.report.pass_count -ne 15) {
    Write-Error "Verification failed: Expected 15/15 PASS, got $($VerifyObj.report.pass_count) PASS."
    exit 3
}

# 4. Multi-Run Empirical Benchmarks
Write-Host "`n[4/6] Executing Multi-Run Scientific Benchmarks (Policy: $Policy)..." -ForegroundColor Yellow
$BenchScript = @"
import json
import hyper_phase_change as hpc

policy_enum = hpc.ExecutionPolicy('$Policy')
bench_res = hpc.UniversalFabricBenchmark.run_full_suite(policy=policy_enum)
md = hpc.UniversalFabricBenchmark.generate_markdown(bench_res)

print(json.dumps({
    'benchmark': bench_res,
    'markdown': md
}))
"@

$BenchOutput = & $PythonCmd -c $BenchScript
$BenchObj = $BenchOutput | ConvertFrom-Json

Write-Host "  Workloads Benchmarked: $($BenchObj.benchmark.workloads_measured)" -ForegroundColor Gray
Write-Host "  Average Suite Speedup: $($BenchObj.benchmark.average_speedup)x" -ForegroundColor Green
Write-Host "  Regressions Detected:  $($BenchObj.benchmark.regressions_detected.Count)" -ForegroundColor $(if ($BenchObj.benchmark.regressions_detected.Count -eq 0) { "Green" } else { "Yellow" })

# 5. Full PyTest Regression Suite
Write-Host "`n[5/6] Executing PyTest Automated Test Batteries..." -ForegroundColor Yellow
$PytestOutput = & $PythonCmd -m pytest -q tests/test_universal_fabric.py tests/test_candidate_workloads_15.py tests/test_computation_escape_advisor.py
Write-Host $PytestOutput -ForegroundColor Gray

if ($LASTEXITCODE -ne 0) {
    Write-Error "Pytest suite execution encountered failures."
    exit $LASTEXITCODE
}

# 6. Generate Reports & Deliverables
Write-Host "`n[6/6] Generating Machine-Readable Reports and Deliverables in '$ReportsDir'..." -ForegroundColor Yellow
if (-not (Test-Path $ReportsDir)) {
    New-Item -ItemType Directory -Path $ReportsDir | Out-Null
}

$TimestampStr = (Get-Date -Format "yyyyMMdd_HHmmss")

# Save Registry
$RegistryPath = Join-Path $ReportsDir "UNIVERSAL_FABRIC_CAPABILITY_REGISTRY.json"
$ProbeJson | Out-File -FilePath $RegistryPath -Encoding utf8
Write-Host "  Saved: $RegistryPath" -ForegroundColor Gray

# Save Certification
$CertPath = Join-Path $ReportsDir "UNIVERSAL_FABRIC_CERTIFICATION.json"
$VerifyObj.certificate | ConvertTo-Json -Depth 10 | Out-File -FilePath $CertPath -Encoding utf8
Write-Host "  Saved: $CertPath" -ForegroundColor Gray

# Save Benchmarks JSON & Markdown
$BenchJsonPath = Join-Path $ReportsDir "UNIVERSAL_FABRIC_BENCHMARKS.json"
$BenchObj.benchmark | ConvertTo-Json -Depth 10 | Out-File -FilePath $BenchJsonPath -Encoding utf8
Write-Host "  Saved: $BenchJsonPath" -ForegroundColor Gray

$BenchMdPath = Join-Path $ReportsDir "UNIVERSAL_FABRIC_BENCHMARKS.md"
$BenchObj.markdown | Out-File -FilePath $BenchMdPath -Encoding utf8
Write-Host "  Saved: $BenchMdPath" -ForegroundColor Gray

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host " ALL GATES PASSED: UNIVERSAL REPLACEMENT FABRIC FULLY VERIFIED" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
exit 0
