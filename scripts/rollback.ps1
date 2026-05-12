#!/usr/bin/env pwsh

# Rollback script for Project HYPER
# Reverts the current deployment to the last known good state by swapping docker tags or restoring from backup.

Write-Host "Starting Rollback for Project HYPER..." -ForegroundColor Yellow

# 1. Stop current containers
docker-compose down

# 2. Revert to previous build if archived
if (Test-Path "./dist_backup") {
    Write-Host "Restoring dist_backup..." -ForegroundColor Green
    Copy-Item -Path "./dist_backup/*" -Destination "./dist" -Recurse -Force
}

# 3. Restart services
docker-compose up -d

# 4. Verify Health
$health = Invoke-RestMethod -Uri "http://localhost:8005/health"
if ($health.status -eq "healthy") {
    Write-Host "Rollback Successful. System is Healthy." -ForegroundColor Green
} else {
    Write-Host "Rollback Warning: System state is $($health.status)" -ForegroundColor Red
}
