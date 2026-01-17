# ByOnco Production Seeding Script
# Usage: .\run_production_seed.ps1
# Make sure to set SUPABASE_SERVICE_ROLE_KEY before running

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ByOnco Production Seeding" -ForegroundColor Cyan
Write-Host "Project: byonco-health" -ForegroundColor Cyan
Write-Host "URL: https://thdpfewpikvunfyllmwj.supabase.co" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set correct Supabase URL
$env:SUPABASE_URL = "https://thdpfewpikvunfyllmwj.supabase.co"
$env:SEED_DIR = "$PSScriptRoot\seed_exports"

# Check if service role key is set
if (-not $env:SUPABASE_SERVICE_ROLE_KEY) {
    Write-Host "ERROR: SUPABASE_SERVICE_ROLE_KEY not set!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set it with:" -ForegroundColor Yellow
    Write-Host '  $env:SUPABASE_SERVICE_ROLE_KEY="your_service_role_key_here"' -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Get it from: Supabase Dashboard → Settings → API → service_role key" -ForegroundColor Yellow
    exit 1
}

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  SUPABASE_URL: $env:SUPABASE_URL"
Write-Host "  SUPABASE_SERVICE_ROLE_KEY: $($env:SUPABASE_SERVICE_ROLE_KEY.Substring(0,20))..."
Write-Host "  SEED_DIR: $env:SEED_DIR"
Write-Host ""

# Check Python
Write-Host "Checking Python environment..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Check requests package
Write-Host "Checking requests package..." -ForegroundColor Green
$requestsCheck = pip show requests 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing requests..." -ForegroundColor Yellow
    pip install requests
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install requests" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ requests installed" -ForegroundColor Gray
}

# Check seed files
Write-Host ""
Write-Host "Checking seed files..." -ForegroundColor Green
$requiredFiles = @("hospitals.json", "doctors.json")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $env:SEED_DIR $file
    if (Test-Path $filePath) {
        $fileSize = (Get-Item $filePath).Length
        Write-Host "  ✅ $file ($([math]::Round($fileSize/1KB, 2)) KB)" -ForegroundColor Gray
    } else {
        Write-Host "  ❌ $file - MISSING" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: Missing required seed files!" -ForegroundColor Red
    Write-Host "Run 'python export_seed_data.py' first" -ForegroundColor Yellow
    exit 1
}

# Run seeder
Write-Host ""
Write-Host "Starting seeding process..." -ForegroundColor Green
Write-Host ""

python supabase_seed.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ Seeding completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run verification SQL in Supabase SQL Editor:" -ForegroundColor Yellow
    Write-Host "   File: byonco-main/supabase/migrations/VERIFY_COUNTS.sql" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Expected results:" -ForegroundColor Yellow
    Write-Host "   - Hospitals: 51" -ForegroundColor Gray
    Write-Host "   - Doctors: 405" -ForegroundColor Gray
    Write-Host "   - Cities: 31" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ Seeding failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error message above." -ForegroundColor Yellow
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Wrong SUPABASE_SERVICE_ROLE_KEY" -ForegroundColor Gray
    Write-Host "  - Wrong SUPABASE_URL" -ForegroundColor Gray
    Write-Host "  - Missing tables (run migrations first)" -ForegroundColor Gray
    Write-Host "  - Network issues" -ForegroundColor Gray
    exit $LASTEXITCODE
}




