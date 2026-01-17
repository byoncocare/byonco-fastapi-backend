# PowerShell script to seed Supabase database
# Usage: .\seed_supabase.ps1

Write-Host "ByOnco Supabase Seeding Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if environment variables are set
if (-not $env:SUPABASE_URL) {
    Write-Host "ERROR: SUPABASE_URL environment variable not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:SUPABASE_URL='https://byonco-health.supabase.co'" -ForegroundColor Yellow
    exit 1
}

if (-not $env:SUPABASE_SERVICE_ROLE_KEY) {
    Write-Host "ERROR: SUPABASE_SERVICE_ROLE_KEY environment variable not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:SUPABASE_SERVICE_ROLE_KEY='your_key_here'" -ForegroundColor Yellow
    exit 1
}

# Set seed directory
$env:SEED_DIR = "$PSScriptRoot\seed_exports"

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  SUPABASE_URL: $env:SUPABASE_URL"
Write-Host "  SEED_DIR: $env:SEED_DIR"
Write-Host ""

# Check if seed_exports directory exists
if (-not (Test-Path $env:SEED_DIR)) {
    Write-Host "ERROR: Seed exports directory not found: $env:SEED_DIR" -ForegroundColor Red
    Write-Host "Run 'python export_seed_data.py' first to generate JSON files" -ForegroundColor Yellow
    exit 1
}

# Check if JSON files exist
$requiredFiles = @("hospitals.json", "doctors.json")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $env:SEED_DIR $file
    if (-not (Test-Path $filePath)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "ERROR: Missing required seed files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host "Run 'python export_seed_data.py' first to generate JSON files" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting seeding process..." -ForegroundColor Green
Write-Host ""

# Run the Python seeding script
python supabase_seed.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Seeding completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Verify data in Supabase SQL Editor:" -ForegroundColor Yellow
    Write-Host "   SELECT COUNT(*) FROM hospitals;" -ForegroundColor Gray
    Write-Host "   SELECT COUNT(*) FROM doctors;" -ForegroundColor Gray
    Write-Host "   SELECT COUNT(DISTINCT city) FROM hospitals;" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "Seeding failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}




