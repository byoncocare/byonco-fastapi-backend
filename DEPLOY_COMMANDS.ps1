# Razorpay Deployment Commands - PowerShell Script
# Run these commands in order

Write-Host "=== BACKEND: Git Commit & Push ===" -ForegroundColor Cyan

# Navigate to backend
cd C:\Users\AJINKYA\byonco-fastapi-backend

# Verify .env is ignored
Write-Host "`nChecking .env is ignored..." -ForegroundColor Yellow
git status | Select-String ".env"
if ($LASTEXITCODE -eq 0) {
    Write-Host "WARNING: .env might be tracked!" -ForegroundColor Red
} else {
    Write-Host "✅ .env is properly ignored" -ForegroundColor Green
}

# Stage Razorpay files
Write-Host "`nStaging Razorpay files..." -ForegroundColor Yellow
git add payments/razorpay.py
git add payments/service.py
git add server.py
git add RAZORPAY_*.md
git add END_TO_END_TESTING.md
git add FINAL_FIX_SUMMARY.md
git add DEPLOYMENT_CHECKLIST.md
git add .gitignore

# Show what will be committed
Write-Host "`nFiles staged for commit:" -ForegroundColor Yellow
git status --short

# Commit
Write-Host "`nCommitting..." -ForegroundColor Yellow
git commit -m "Razorpay backend payments production-ready"

# Verify remote
Write-Host "`nRemote repository:" -ForegroundColor Yellow
git remote -v

# Ask for confirmation before push
Write-Host "`nReady to push to origin/main. Continue? (Y/N)" -ForegroundColor Yellow
$confirm = Read-Host
if ($confirm -eq "Y" -or $confirm -eq "y") {
    git push origin main
    Write-Host "✅ Backend pushed to GitHub" -ForegroundColor Green
} else {
    Write-Host "Push cancelled. Run 'git push origin main' manually when ready." -ForegroundColor Yellow
}

Write-Host "`n=== FRONTEND: Git Commit & Push ===" -ForegroundColor Cyan

# Navigate to frontend root
cd C:\Users\AJINKYA\ByOnco

# Verify .env is ignored
Write-Host "`nChecking .env is ignored..." -ForegroundColor Yellow
git status | Select-String ".env"
if ($LASTEXITCODE -eq 0) {
    Write-Host "WARNING: .env might be tracked!" -ForegroundColor Red
} else {
    Write-Host "✅ .env is properly ignored" -ForegroundColor Green
}

# Stage checkout/Razorpay files
Write-Host "`nStaging checkout/Razorpay files..." -ForegroundColor Yellow
git add src/products/vayu/pages/VayuCheckoutPage.jsx
git add src/products/vayu/pages/VayuCheckoutSuccess.jsx
git add src/products/vayu/pages/VayuOrderPage.jsx
git add src/products/vayu/components/order/
git add src/products/vayu/utils/
git add src/App.js
git add .gitignore

# Show what will be committed
Write-Host "`nFiles staged for commit:" -ForegroundColor Yellow
git status --short

# Commit
Write-Host "`nCommitting..." -ForegroundColor Yellow
git commit -m "Checkout flow + Razorpay integration"

# Verify remote
Write-Host "`nRemote repository:" -ForegroundColor Yellow
git remote -v

# Ask for confirmation before push
Write-Host "`nReady to push to origin/main. Continue? (Y/N)" -ForegroundColor Yellow
$confirm = Read-Host
if ($confirm -eq "Y" -or $confirm -eq "y") {
    git push origin main
    Write-Host "✅ Frontend pushed to GitHub" -ForegroundColor Green
} else {
    Write-Host "Push cancelled. Run 'git push origin main' manually when ready." -ForegroundColor Yellow
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "1. Deploy backend to Render (see DEPLOYMENT_CHECKLIST.md)" -ForegroundColor White
Write-Host "2. Deploy frontend to Vercel (see DEPLOYMENT_CHECKLIST.md)" -ForegroundColor White
Write-Host "3. Set environment variables in Render and Vercel" -ForegroundColor White
Write-Host "4. Test endpoints using curl commands in DEPLOYMENT_CHECKLIST.md" -ForegroundColor White

