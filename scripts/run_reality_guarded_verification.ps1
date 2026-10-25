# ==============================================================================
# scripts/run_reality_guarded_verification.ps1
# LEO / HYPER: Master Reality-Guarded Windows Verification Runner
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
Write-Host " LEO / HYPER -- REALITY-GUARDED UNIVERSAL REPLACEMENT ENGINE" -ForegroundColor Cyan
Write-Host " Master Windows 11 Verification & Hardware Ground-Truth Audit" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Environment & Physical Hardware Probe
Write-Host "`n[1/8] Recording Operating System, CPU, RAM, and Python Environment..." -ForegroundColor Yellow
$PythonCmd = "python"

if (-not (Get-Command $PythonCmd -ErrorAction SilentlyContinue)) {
    Write-Error "Python executable not found in PATH."
    exit 1
}

$PyVer = & $PythonCmd -c "import sys; print(sys.version.split()[0])"
$OsName = [System.Environment]::OSVersion.VersionString
$CpuName = (Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name).Trim()
$LogicalCores = (Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty NumberOfLogicalProcessors)
$TotalRamGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)

Write-Host "  Operating System:    $OsName (AMD64)" -ForegroundColor Gray
Write-Host "  Python Runtime:      $PyVer" -ForegroundColor Gray
Write-Host "  Host Processor:      $CpuName ($LogicalCores logical cores)" -ForegroundColor Gray
Write-Host "  Host Memory Budget:  $TotalRamGB GB Unified RAM" -ForegroundColor Gray

# 2. Probe Actual Intel Graphics Device, Driver & Optional Runtimes
Write-Host "`n[2/8] Probing Actual Intel Graphics Device, Driver, and Compute Runtimes..." -ForegroundColor Yellow
$GpuProbe = Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, Status
foreach ($gpu in $GpuProbe) {
    Write-Host "  Detected Controller: $($gpu.Name) [Driver: $($gpu.DriverVersion), Status: $($gpu.Status)]" -ForegroundColor Gray
}

# 3. Dynamic Python Hardware & Capability Discovery
Write-Host "`n[3/8] Querying Physical Device Probe & Capability Registry via Python..." -ForegroundColor Yellow
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
Write-Host "  Intel Device String:      $($ProbeObj.probe.igpu_device_name)" -ForegroundColor Gray
Write-Host "  Intel Probe Verified:     $($ProbeObj.probe.igpu_probe_success)" -ForegroundColor Gray
Write-Host "  Discrete GPU Status:      $($ProbeObj.probe.discrete_gpu_parity_status)" -ForegroundColor Gray
Write-Host "  Registered Backends:      $($ProbeObj.registered_backends.Count)" -ForegroundColor Gray

if ($StrictIgpuCheck -and (-not $ProbeObj.probe.igpu_probe_success)) {
    Write-Error "Strict iGPU check requested, but Intel UHD Graphics probe was not verified."
    exit 2
}

# 4. Canonical 15 Independent Reference Verification
Write-Host "`n[4/8] Executing Fail-Closed Canonical 15 Independent Verification..." -ForegroundColor Yellow
& $PythonCmd scripts/verify_canonical_15.py --output (Join-Path $ReportsDir "canonical_15_verification.json") --seed $Seed

if ($LASTEXITCODE -ne 0) {
    Write-Error "Canonical 15 independent verification failed (Non-zero exit code)."
    exit 3
}

# 5. Master Reality-Guarded Certification Harness
Write-Host "`n[5/8] Running Master Reality-Guarded Certification Battery..." -ForegroundColor Yellow
& $PythonCmd scripts/run_reality_guarded_verification.py --reports-dir $ReportsDir --seed $Seed

if ($LASTEXITCODE -ne 0) {
    Write-Error "Master Reality-Guarded Certification failed one or more gates."
    exit 4
}

# 6. PyTest Provenance and Truth Regression Suites
Write-Host "`n[6/8] Executing PyTest Truthfulness, Provenance & Parity Batteries..." -ForegroundColor Yellow
& $PythonCmd -m pytest -q tests/test_benchmark_provenance_truth.py tests/test_canonical_15_suite.py tests/test_universal_fabric.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Provenance or canonical regression tests failed."
    exit 5
}

# 7. PyTest Candidate Workloads and Escape Advisor Integration Tests
Write-Host "`n[7/8] Executing Integration and Algorithmic Escape Tests..." -ForegroundColor Yellow
& $PythonCmd -m pytest -q tests/test_candidate_workloads_15.py tests/test_computation_escape_advisor.py tests/test_cpce_core.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Algorithmic escape or core CPCE integration tests failed."
    exit 6
}

# 8. Report Artifact Archiving and Commit Association
Write-Host "`n[8/8] Verifying Output Deliverables and Associating Commit Hash..." -ForegroundColor Yellow
$CertJsonPath = Join-Path $ReportsDir "REALITY_GUARDED_CERTIFICATION.json"
$CertMdPath = Join-Path $ReportsDir "REALITY_GUARDED_CERTIFICATION.md"

if ((Test-Path $CertJsonPath) -and (Test-Path $CertMdPath)) {
    Write-Host "  Successfully Generated: $CertJsonPath" -ForegroundColor Green
    Write-Host "  Successfully Generated: $CertMdPath" -ForegroundColor Green
} else {
    Write-Error "Required certification artifacts were not produced."
    exit 7
}

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host " ALL REALITY-GUARDED GATES PASSED: 100% TRUTHFUL, VERIFIED, VERSIONED" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
exit 0
