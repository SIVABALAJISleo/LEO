# PowerShell script to onboard LEO AI API tests in TestSprite
# Performs project registration, test registration, and smoke execution.

Write-Host "====================================================" -ForegroundColor Green
Write-Host "       TestSprite Automatic Onboarding Tool         " -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""

# 1. Create a backend project in TestSprite
Write-Host "[1/3] Creating TestSprite project 'LEO AI Backend'..." -ForegroundColor Cyan
$projectOutput = testsprite project create --type backend --name "LEO AI Backend"

if ($LASTEXITCODE -ne 0 -or -not $projectOutput) {
    Write-Host "[ERROR] Failed to create project in TestSprite. Make sure you ran .\setup_testsprite.ps1 first." -ForegroundColor Red
    Exit
}

# Extract projectId from output
$projectId = ""
if ($projectOutput -match "projectId:\s*([a-zA-Z0-9_-]+)") {
    $projectId = $Matches[1]
} else {
    # Fallback to scanning lines
    foreach ($line in $projectOutput) {
        if ($line -match "id:\s*([a-zA-Z0-9_-]+)") {
            $projectId = $Matches[1]
            break
        }
    }
}

if (-not $projectId) {
    Write-Host "[ERROR] Could not extract projectId from output:" -ForegroundColor Red
    Write-Host $projectOutput
    Exit
}

Write-Host "[OK] Project created successfully. Project ID: $projectId" -ForegroundColor Green
Write-Host ""

# 2. Register the tests
Write-Host "[2/3] Registering backend tests in TestSprite..." -ForegroundColor Cyan

# Test 1: Chat Completion
Write-Host "Registering 'test_openai_completion'..." -ForegroundColor Gray
$test1Output = testsprite test create --type backend --name "OpenAI Chat Completion API" --project $projectId --code-file ./testsprite_tests/test_openai_completion.py

# Test 2: System Status
Write-Host "Registering 'test_leo_status'..." -ForegroundColor Gray
$test2Output = testsprite test create --type backend --name "LEO System Status API" --project $projectId --code-file ./testsprite_tests/test_leo_status.py

Write-Host "[OK] Tests registered successfully." -ForegroundColor Green
Write-Host ""

# 3. Prompt for smoke execution
Write-Host "[3/3] Execution options" -ForegroundColor Cyan
Write-Host "To run these tests, you must specify a publicly accessible URL." -ForegroundColor Yellow
Write-Host "If you started your local tunnel via .\start_tunnel.bat, paste the public HTTPS URL here." -ForegroundColor Yellow
Write-Host "(Press Enter to skip execution and only view your onboarded project)" -ForegroundColor Gray
Write-Host ""

$targetUrl = Read-Host "Target URL (e.g. https://xxxx.trycloudflare.com)"

if ($targetUrl.Trim() -ne "") {
    Write-Host ""
    Write-Host "Launching TestSuite run on target: $targetUrl ..." -ForegroundColor Cyan
    testsprite test run --all --project $projectId --target-url $targetUrl --wait
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 All TestSprite tests PASSED successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Test run failed or blocked. Run 'testsprite test list --project $projectId' to investigate." -ForegroundColor Red
    }
} else {
    Write-Host "Skipping execution. Your tests are successfully onboarded!" -ForegroundColor Green
    Write-Host "You can run them later using: " -ForegroundColor Gray
    Write-Host "  testsprite test run --all --project $projectId --target-url <YOUR_PUBLIC_TUNNEL_URL> --wait" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host "TestSprite project onboarding complete!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
