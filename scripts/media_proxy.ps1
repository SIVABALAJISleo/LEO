#!/usr/bin/env pwsh

# Media Proxy Workflow for Project HYPER
# Transcodes heavy media in the background and provides lightweight proxies for the UI.

param (
    [string]$InputFile,
    [string]$OutputFolder = "./proxies"
)

if (!(Test-Path $OutputFolder)) { New-Item -ItemType Directory -Path $OutputFolder }

$BaseName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$ProxyPath = "$OutputFolder/$BaseName`_proxy.mp4"

Write-Host "Generating Proxy for $InputFile..." -ForegroundColor Cyan

# Use ffmpeg to create a low-res proxy
& ffmpeg -i $InputFile -vf "scale=-2:360" -c:v libx264 -crf 28 -preset fast -y $ProxyPath

Write-Host "Proxy created at $ProxyPath" -ForegroundColor Green
