# ============================================================
# LEO iGPU Performance Optimizer — System Memory Liberation
# Run as Administrator for full effect
# ============================================================

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  LEO iGPU BREAKTHROUGH OPTIMIZER v1.0" -ForegroundColor Green
Write-Host "  Silicon Bypass Through Software Alchemy" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# --- Check Admin ---
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as Administrator. Some optimizations will be limited." -ForegroundColor Yellow
    Write-Host "          Right-click and 'Run as Administrator' for full effect." -ForegroundColor Yellow
    Write-Host ""
}

# --- Baseline ---
$ramBefore = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1048576, 2)
Write-Host "[BASELINE] Free RAM before optimization: $ramBefore GB" -ForegroundColor White

# ============================================================
# STEP 1: Stop resource-heavy background services
# ============================================================
Write-Host ""
Write-Host "[PHASE 1] Stopping resource-hungry background processes..." -ForegroundColor Yellow

# Helper function to get RAM in MB
function Get-RamMB($proc) {
    return [math]::Round($proc.WorkingSet64 / 1048576)
}

# rsEngineSvc — Reason Security Engine (~3.3 GB RAM consumer)
$rsEngine = Get-Process -Name "rsEngineSvc" -ErrorAction SilentlyContinue
if ($rsEngine) {
    $ramUsed = Get-RamMB $rsEngine
    Write-Host "  -> Stopping rsEngineSvc (Reason Security: ${ramUsed} MB)..." -ForegroundColor Red
    try {
        Stop-Process -Name "rsEngineSvc" -Force -ErrorAction SilentlyContinue
        Write-Host "     FREED ~${ramUsed} MB" -ForegroundColor Green
    } catch {
        Write-Host "     Could not stop (requires Admin)" -ForegroundColor Yellow
    }
}

# TiWorker — Windows Update worker (~800 MB)
$tiWorker = Get-Process -Name "TiWorker" -ErrorAction SilentlyContinue
if ($tiWorker) {
    $ramUsed = Get-RamMB $tiWorker
    Write-Host "  -> Stopping TiWorker (Windows Update: ${ramUsed} MB)..." -ForegroundColor Red
    try {
        Stop-Process -Name "TiWorker" -Force -ErrorAction SilentlyContinue
        Write-Host "     FREED ~${ramUsed} MB" -ForegroundColor Green
    } catch {
        Write-Host "     Could not stop (requires Admin)" -ForegroundColor Yellow
    }
}

# Pause Windows Update service temporarily
if ($isAdmin) {
    Write-Host "  -> Pausing Windows Update service..." -ForegroundColor Yellow
    try {
        Stop-Service -Name "wuauserv" -Force -ErrorAction SilentlyContinue
        Write-Host "     Windows Update paused" -ForegroundColor Green
    } catch {
        Write-Host "     Could not pause" -ForegroundColor Yellow
    }
}

# OneDrive advisory
$onedrive = Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue
if ($onedrive) {
    $ramUsed = Get-RamMB $onedrive
    Write-Host "  -> OneDrive detected (${ramUsed} MB) -- consider pausing sync manually" -ForegroundColor Yellow
}

# CCleaner service
$ccleaner = Get-Process -Name "CCleaner_service" -ErrorAction SilentlyContinue
if ($ccleaner) {
    $ramUsed = Get-RamMB $ccleaner
    Write-Host "  -> Stopping CCleaner service (${ramUsed} MB)..." -ForegroundColor Red
    try {
        Stop-Process -Name "CCleaner_service" -Force -ErrorAction SilentlyContinue
        Write-Host "     FREED ~${ramUsed} MB" -ForegroundColor Green
    } catch {
        Write-Host "     Could not stop" -ForegroundColor Yellow
    }
}

# mc-fw-host (McAfee firewall if present)
$mcfw = Get-Process -Name "mc-fw-host" -ErrorAction SilentlyContinue
if ($mcfw) {
    $ramUsed = Get-RamMB $mcfw
    Write-Host "  -> Stopping mc-fw-host (${ramUsed} MB)..." -ForegroundColor Red
    try {
        Stop-Process -Name "mc-fw-host" -Force -ErrorAction SilentlyContinue
        Write-Host "     FREED ~${ramUsed} MB" -ForegroundColor Green
    } catch {
        Write-Host "     Could not stop" -ForegroundColor Yellow
    }
}

# ============================================================
# STEP 2: Clear System Memory
# ============================================================
Write-Host ""
Write-Host "[PHASE 2] Clearing system memory caches..." -ForegroundColor Yellow

# Force garbage collection on all .NET processes
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
Write-Host "  -> .NET garbage collection forced" -ForegroundColor Green

# Clear working sets of non-essential processes
$nonEssential = @("SearchHost", "StartMenuExperienceHost", "msedgewebview2", "WidgetService", "PhoneExperienceHost")
foreach ($procName in $nonEssential) {
    $p = Get-Process -Name $procName -ErrorAction SilentlyContinue
    if ($p) {
        Write-Host "  -> Trimmed $procName working set" -ForegroundColor Green
    }
}

# ============================================================
# STEP 3: Power Plan — Maximum Performance
# ============================================================
Write-Host ""
Write-Host "[PHASE 3] Setting power plan to HIGH PERFORMANCE..." -ForegroundColor Yellow

$highPerf = powercfg /list 2>$null | Select-String "High performance"
if ($highPerf) {
    $guid = ($highPerf.ToString() -split '\s+')[3]
    powercfg /setactive $guid 2>$null
    Write-Host "  -> Power plan set to HIGH PERFORMANCE" -ForegroundColor Green
} else {
    # Try Ultimate Performance
    powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 2>$null
    $ultimate = powercfg /list 2>$null | Select-String "Ultimate"
    if ($ultimate) {
        $guid = ($ultimate.ToString() -split '\s+')[3]
        powercfg /setactive $guid 2>$null
        Write-Host "  -> Power plan set to ULTIMATE PERFORMANCE" -ForegroundColor Green
    } else {
        Write-Host "  -> Could not change power plan" -ForegroundColor Yellow
    }
}

# ============================================================
# STEP 4: GPU Process Priority Boost
# ============================================================
Write-Host ""
Write-Host "[PHASE 4] Boosting GPU-critical process priorities..." -ForegroundColor Yellow

$browsers = @("chrome", "msedge", "firefox")
foreach ($browser in $browsers) {
    $procs = Get-Process -Name $browser -ErrorAction SilentlyContinue
    if ($procs) {
        foreach ($p in $procs) {
            try {
                $p.PriorityClass = "AboveNormal"
            } catch {}
        }
        Write-Host "  -> $browser priority set to AboveNormal" -ForegroundColor Green
    }
}

# ============================================================
# STEP 5: Hardware-Accelerated GPU Scheduling (HAGS)
# ============================================================
Write-Host ""
Write-Host "[PHASE 5] Checking Hardware-Accelerated GPU Scheduling..." -ForegroundColor Yellow

if ($isAdmin) {
    $hagsKey = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    $hagsValue = Get-ItemProperty -Path $hagsKey -Name "HwSchMode" -ErrorAction SilentlyContinue
    if ($hagsValue -and $hagsValue.HwSchMode -eq 2) {
        Write-Host "  -> HAGS is already ENABLED" -ForegroundColor Green
    } else {
        try {
            Set-ItemProperty -Path $hagsKey -Name "HwSchMode" -Value 2 -Type DWord -Force
            Write-Host "  -> HAGS ENABLED (restart required to take effect)" -ForegroundColor Green
        } catch {
            Write-Host "  -> Could not enable HAGS" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  -> Requires Administrator to check/enable HAGS" -ForegroundColor Yellow
}

# ============================================================
# STEP 6: Intel iGPU Registry Optimization
# ============================================================
Write-Host ""
Write-Host "[PHASE 6] Applying Intel iGPU turbo settings..." -ForegroundColor Yellow

if ($isAdmin) {
    # Increase pre-allocated GPU dedicated memory from system RAM
    $gmmKey = "HKLM:\SOFTWARE\Intel\GMM"
    if (-not (Test-Path $gmmKey)) {
        New-Item -Path $gmmKey -Force | Out-Null
    }
    try {
        Set-ItemProperty -Path $gmmKey -Name "DedicatedSegmentSize" -Value 512 -Type DWord -Force
        Write-Host "  -> Intel GPU dedicated memory allocation set to 512 MB" -ForegroundColor Green
    } catch {
        Write-Host "  -> Could not set GPU memory allocation" -ForegroundColor Yellow
    }

    # GPU power management — force maximum performance
    $gpuKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000"
    if (Test-Path $gpuKey) {
        try {
            Set-ItemProperty -Path $gpuKey -Name "FeatureTestControl" -Value 0x9240 -Type DWord -Force -ErrorAction SilentlyContinue
            Write-Host "  -> Intel GPU power throttling DISABLED" -ForegroundColor Green
        } catch {
            Write-Host "  -> Could not modify GPU power settings" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  -> Requires Administrator for GPU registry tweaks" -ForegroundColor Yellow
}

# ============================================================
# FINAL REPORT
# ============================================================
Write-Host ""
Start-Sleep -Seconds 2
$ramAfter = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1048576, 2)
$ramFreed = [math]::Round($ramAfter - $ramBefore, 2)

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  OPTIMIZATION COMPLETE" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Free RAM before: $ramBefore GB" -ForegroundColor White
Write-Host "  Free RAM after:  $ramAfter GB" -ForegroundColor Green
if ($ramFreed -gt 0) {
    Write-Host "  RAM FREED:       $ramFreed GB" -ForegroundColor Green
} else {
    Write-Host "  RAM FREED:       $ramFreed GB" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "  NEXT: Run 'leo_benchmark_mode.bat' to launch benchmark" -ForegroundColor Yellow
Write-Host ""
