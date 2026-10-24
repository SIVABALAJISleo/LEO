# scripts/run_hyper_immediate_verification.ps1
# ===============================================
# Automated End-to-End Master Verification Pipeline on Windows 11.
# Runs:
# 1. Python version check
# 2. Hardware Capability Probe (CPU + Intel UHD iGPU)
# 3. Canonical 15-Workload Independent Verification
# 4. Pytest suite (Computation Escape Advisor + 15 Candidate Workloads)
# 5. CompileAll bytecode validation

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " LEO/HYPER - Immediate Implementation and Verification Master Suite" -ForegroundColor Cyan
Write-Host " Target: Lenovo IdeaPad Slim 3 15IAH8 | Intel Core i5 | Windows 11" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Step 1: Python Version Check
Write-Host "`n[STEP 1/5] Checking Python Environment..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python check failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# Step 2: Hardware Capability Probe
Write-Host "`n[STEP 2/5] Running Hardware Capability and Device Probe..." -ForegroundColor Yellow
python scripts/probe_hyper_devices.py --output reports/hardware_capability_probe.json
if ($LASTEXITCODE -ne 0) {
    Write-Host "Hardware probe failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# Step 3: Canonical 15-Workload Verification
Write-Host "`n[STEP 3/5] Running Canonical 15-Workload Independent Verification..." -ForegroundColor Yellow
python scripts/verify_canonical_15.py --output reports/canonical_15_verification.json
if ($LASTEXITCODE -ne 0) {
    Write-Host "Canonical 15 verification failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# Step 4: Pytest Suite Execution
Write-Host "`n[STEP 4/5] Executing Pytest Suites (Escape Advisor + 15 Workloads)..." -ForegroundColor Yellow
python -m pytest -q tests/test_computation_escape_advisor.py tests/test_candidate_workloads_15.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pytest suite failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# Step 5: Bytecode Compilation Check
Write-Host "`n[STEP 5/5] Compiling and Validating Bytecode Integrity..." -ForegroundColor Yellow
python -m compileall -q hyper/research_engine/computation_escape_advisor.py scripts/probe_hyper_devices.py scripts/verify_canonical_15.py tests/test_computation_escape_advisor.py tests/test_candidate_workloads_15.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Bytecode compilation failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host " [SUCCESS] All 5 Master Verification Steps Passed Cleanly (15/15 PASS)" -ForegroundColor Green
Write-Host " Evidence Reports:" -ForegroundColor Green
Write-Host "   - reports/hardware_capability_probe.json" -ForegroundColor Green
Write-Host "   - reports/canonical_15_verification.json" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
exit 0
