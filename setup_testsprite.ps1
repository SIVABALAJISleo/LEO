# PowerShell script to set up TestSprite CLI
# Execute this to install and authenticate TestSprite on your machine.

Write-Host "====================================================" -ForegroundColor Green
Write-Host "       TestSprite CLI Setup & Verification          " -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""

# Step 1: Install @testsprite/testsprite-cli globally
Write-Host "[1/3] Installing @testsprite/testsprite-cli globally..." -ForegroundColor Cyan
npm install -g @testsprite/testsprite-cli

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] npm install failed. Please make sure Node.js and npm are installed." -ForegroundColor Red
    Exit
}

# Step 2: Initialize testsprite setup
Write-Host ""
Write-Host "[2/3] Running 'testsprite setup'..." -ForegroundColor Cyan
Write-Host "Please paste your API key when prompted:" -ForegroundColor Yellow
Write-Host "  sk-user-Cun0GGzgFhL11K7y8nkcpzeosh_xl46LAavoWip3mX_h1g_1ZdYX4CLIw_Ew4VyKY4_1tLQN_9oX-xaZrCohFVAHF7skQlrtfMVWmmu5T_sSMqq35hg4vep300nlpa_2jLU" -ForegroundColor Green
Write-Host ""

testsprite setup

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] TestSprite setup failed." -ForegroundColor Red
    Exit
}

# Step 3: Run diagnostics
Write-Host ""
Write-Host "[3/3] Checking TestSprite connection..." -ForegroundColor Cyan
testsprite doctor

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host "TestSprite CLI setup complete! You can now ask the  " -ForegroundColor Green
Write-Host "IDE agent to generate and run autonomous tests.     " -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
