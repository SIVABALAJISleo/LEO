
$root = "C:\Users\sivab\OneDrive\Documents\HYPER\remix-of-remix-of-remix-of-nvidia-inspired-design-main"
$targetDirs = @("backend", "adaptive_self_correcting_system", "data", "scripts", "tests", ".github", "public")
$includeExts = @("*.py", "*.yml", "*.yaml", "*.json", "*.md", "*.txt", "*.toml", "*.ts", "*.tsx", "*.js", "*.html", "*.css", "*.sh", "*.ps1", "*.bat")

# Content replacement
foreach ($dir in $targetDirs) {
    $dirPath = Join-Path $root $dir
    if (Test-Path $dirPath) {
        $files = Get-ChildItem -Path $dirPath -Recurse -Include $includeExts
        foreach ($f in $files) {
            $content = [System.IO.File]::ReadAllText($f.FullName)
            $original = $content
            $content = $content -creplace 'Project HYPER', 'Project HYPER'
            $content = $content -creplace 'project_hyper', 'project_hyper'
            $content = $content -creplace 'project-hyper', 'project-hyper'
            $content = $content -creplace 'SIVABALAJISleo/HYPER', 'SIVABALAJISleo/HYPER'
            $content = $content -creplace 'HYPER', 'HYPER'
            if ($content -ne $original) {
                [System.IO.File]::WriteAllText($f.FullName, $content)
                Write-Host "Updated content: $($f.FullName)"
            }
        }
    }
}

# File renaming (do this after content replacement to ensure strings are updated)
foreach ($dir in $targetDirs) {
    $dirPath = Join-Path $root $dir
    if (Test-Path $dirPath) {
        $filesToRename = Get-ChildItem -Path $dirPath -Recurse -File | Where-Object { $_.Name -match 'leo' }
        foreach ($f in $filesToRename) {
            $newName = $f.Name -creplace 'project_hyper', 'project_hyper' -creplace 'leo_', 'hyper_' -creplace '_leo', '_hyper' -creplace 'leo', 'hyper'
            Rename-Item -Path $f.FullName -NewName $newName -Force
            Write-Host "Renamed file: $($f.FullName) -> $newName"
        }
    }
}

# Directory renaming (deepest first)
foreach ($dir in $targetDirs) {
    $dirPath = Join-Path $root $dir
    if (Test-Path $dirPath) {
        $dirsToRename = Get-ChildItem -Path $dirPath -Recurse -Directory | Where-Object { $_.Name -match 'leo' } | Sort-Object { $_.FullName.Length } -Descending
        foreach ($d in $dirsToRename) {
            $newName = $d.Name -creplace 'project_hyper', 'project_hyper' -creplace 'leo', 'hyper'
            Rename-Item -Path $d.FullName -NewName $newName -Force
            Write-Host "Renamed dir: $($d.FullName) -> $newName"
        }
    }
}
