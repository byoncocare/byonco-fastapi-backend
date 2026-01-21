# PowerShell script to run common backend tasks
# Usage: .\scripts\run.ps1 [command]

param(
    [Parameter(Position=0)]
    [ValidateSet("install", "run", "run-prod", "test", "verify", "seed", "admin", "help")]
    [string]$Command = "help"
)

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

function Start-DevServer {
    Write-Host "Starting development server..." -ForegroundColor Cyan
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Start-ProdServer {
    Write-Host "Starting production server..." -ForegroundColor Cyan
    uvicorn app.main:app --host 0.0.0.0 --port 8000
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Cyan
    python scripts/testing/test_server.py
    python scripts/testing/test_endpoints.py
    python scripts/testing/test_new_modules.py
}

function Verify-Routes {
    Write-Host "Verifying routes..." -ForegroundColor Cyan
    python scripts/verification/verify_routes.py
}

function Seed-Database {
    Write-Host "Seeding database..." -ForegroundColor Cyan
    python scripts/seeding/seed_database.py
}

function Create-AdminUser {
    Write-Host "Creating admin user..." -ForegroundColor Cyan
    python scripts/admin/create_admin_user.py
}

function Show-Help {
    Write-Host "`nByOnco Backend - Available Commands:`n" -ForegroundColor Yellow
    Write-Host "  .\scripts\run.ps1 install    - Install dependencies"
    Write-Host "  .\scripts\run.ps1 run        - Run development server"
    Write-Host "  .\scripts\run.ps1 run-prod   - Run production server"
    Write-Host "  .\scripts\run.ps1 test       - Run all tests"
    Write-Host "  .\scripts\run.ps1 verify     - Verify API routes"
    Write-Host "  .\scripts\run.ps1 seed       - Seed database"
    Write-Host "  .\scripts\run.ps1 admin      - Create admin user"
    Write-Host "  .\scripts\run.ps1 help       - Show this help`n"
}

switch ($Command) {
    "install" { Install-Dependencies }
    "run" { Start-DevServer }
    "run-prod" { Start-ProdServer }
    "test" { Run-Tests }
    "verify" { Verify-Routes }
    "seed" { Seed-Database }
    "admin" { Create-AdminUser }
    default { Show-Help }
}
