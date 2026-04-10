#!/usr/bin/env pwsh

# Chaos Engine for Project HYPER
# Tests system resilience by toggling services and checking health.

$API_URL = "http://localhost:8005/health"

function Check-Health {
    try {
        $health = Invoke-RestMethod -Uri $API_URL -ErrorAction Stop
        return $health.status
    } catch {
        return "DOWN"
    }
}

Write-Host "--- Chaos Test Started ---" -ForegroundColor Cyan

# 1. Baseline
$status = Check-Health
Write-Host "Initial Status: $status"

# 2. Simulate Error Pressure (via middleware logic if we had a trigger, or just stop service)
Write-Host "Stopping Services..." -ForegroundColor Yellow
docker-compose stop backend

$status = Check-Health
Write-Host "Status after Stop: $status" # Expected: DOWN

# 3. Restore
Write-Host "Restoring Services..." -ForegroundColor Green
docker-compose start backend
Start-Sleep -Seconds 5

$status = Check-Health
Write-Host "Status after Restore: $status" # Expected: healthy

Write-Host "--- Chaos Test Complete ---" -ForegroundColor Cyan
