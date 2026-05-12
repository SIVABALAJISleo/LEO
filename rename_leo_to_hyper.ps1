
# ============================================================
# rename_leo_to_hyper.ps1
# Renames all occurrences of HYPER -> HYPER in source files
# and renames leo_* files/dirs to hyper_* / project_hyper* -> project_hyper*
# Skips: node_modules, venv, venv_old, venv_py311, dist, .git, test_venv
# ============================================================

$root = "C:\Users\sivab\OneDrive\Documents\HYPER\HYPER-main"
$excludeDirPatterns = @("\\node_modules\\","\\venv\\","\\venv_old\\","\\venv_py311\\","\\dist\\","\\.git\\","\\test_venv\\","\\__pycache__\\")
$includeExts = @("*.py","*.yml","*.yaml","*.json","*.md","*.txt","*.toml","*.ts","*.tsx","*.js","*.html","*.css","*.sh","*.ps1","*.bat","*.cfg","*.ini","*.env","*.example")

Write-Host "=== STEP 1: Replacing HYPER in file CONTENTS ===" -ForegroundColor Cyan

$files = Get-ChildItem -Recurse -Path $root -Include $includeExts | Where-Object {
    $path = $_.FullName
    $skip = $false
    foreach ($pat in $excludeDirPatterns) {
        if ($path -match [regex]::Escape($pat)) { $skip = $true; break }
    }
    -not $skip
}

$contentCount = 0
foreach ($f in $files) {
    try {
        $content = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    } catch { continue }
    $original = $content

    # Ordered replacements — most specific first
    $content = $content -creplace 'Project HYPER', 'Project HYPER'
    $content = $content -creplace 'project_hyper', 'project_hyper'
    $content = $content -creplace 'project-hyper', 'project-hyper'
    $content = $content -creplace 'SIVABALAJISleo/HYPER', 'SIVABALAJISleo/HYPER'
    $content = $content -creplace '/HYPER\.git', '/HYPER.git'
    $content = $content -creplace 'work/HYPER/HYPER', 'work/HYPER/HYPER'
    $content = $content -creplace '"HYPER"', '"HYPER"'
    $content = $content -creplace "'HYPER'", "'HYPER'"
    $content = $content -creplace '\bLEO\b', 'HYPER'

    if ($content -ne $original) {
        [System.IO.File]::WriteAllText($f.FullName, $content, [System.Text.Encoding]::UTF8)
        Write-Host "  [CONTENT] $($f.Name)" -ForegroundColor Green
        $contentCount++
    }
}
Write-Host "  -> $contentCount file(s) updated" -ForegroundColor Yellow

Write-Host ""
Write-Host "=== STEP 2: Renaming FILES with 'leo' in name ===" -ForegroundColor Cyan

$filesToRename = Get-ChildItem -Recurse -Path $root -File | Where-Object {
    $path = $_.FullName
    $skip = $false
    foreach ($pat in $excludeDirPatterns) {
        if ($path -match [regex]::Escape($pat)) { $skip = $true; break }
    }
    (-not $skip) -and ($_.Name -match 'leo' -or $_.Name -match 'HYPER')
}

$fileRenameCount = 0
foreach ($f in $filesToRename) {
    $newName = $f.Name -creplace 'project_hyper', 'project_hyper' -creplace 'leo_', 'hyper_' -creplace '_leo', '_hyper' -creplace 'HYPER', 'HYPER' -creplace 'leo', 'hyper'
    if ($newName -ne $f.Name) {
        Rename-Item -Path $f.FullName -NewName $newName -Force
        Write-Host "  [FILE] $($f.Name) -> $newName" -ForegroundColor Green
        $fileRenameCount++
    }
}
Write-Host "  -> $fileRenameCount file(s) renamed" -ForegroundColor Yellow

Write-Host ""
Write-Host "=== STEP 3: Renaming DIRECTORIES with 'leo' in name ===" -ForegroundColor Cyan

# Process deepest dirs first to avoid path invalidation
$dirsToRename = Get-ChildItem -Recurse -Path $root -Directory | Where-Object {
    $path = $_.FullName
    $skip = $false
    foreach ($pat in $excludeDirPatterns) {
        if ($path -match [regex]::Escape($pat)) { $skip = $true; break }
    }
    (-not $skip) -and ($_.Name -match 'leo' -or $_.Name -match 'HYPER')
} | Sort-Object { $_.FullName.Length } -Descending

$dirRenameCount = 0
foreach ($d in $dirsToRename) {
    if (-not (Test-Path $d.FullName)) { continue }  # already renamed as child
    $newName = $d.Name -creplace 'project_hyper', 'project_hyper' -creplace 'leo_', 'hyper_' -creplace '_leo', '_hyper' -creplace 'HYPER', 'HYPER' -creplace 'leo', 'hyper'
    if ($newName -ne $d.Name) {
        Rename-Item -Path $d.FullName -NewName $newName -Force
        Write-Host "  [DIR]  $($d.Name) -> $newName" -ForegroundColor Green
        $dirRenameCount++
    }
}
Write-Host "  -> $dirRenameCount director(ies) renamed" -ForegroundColor Yellow

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Cyan
Write-Host "Content changes: $contentCount | Files renamed: $fileRenameCount | Dirs renamed: $dirRenameCount" -ForegroundColor White
