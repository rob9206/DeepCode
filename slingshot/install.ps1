# Slingshot Stock Scanner - Windows Installation Script
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎯 Slingshot Stock Scanner - Installer" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host "`nChecking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ Found pip" -ForegroundColor Green
} catch {
    Write-Host "✗ pip not found!" -ForegroundColor Red
    Write-Host "Installing pip..." -ForegroundColor Yellow
    python -m ensurepip --default-pip
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes...`n" -ForegroundColor Gray

pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n✗ Failed to install dependencies" -ForegroundColor Red
    Write-Host "Try running manually: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Test installation
Write-Host "`nTesting installation..." -ForegroundColor Yellow
python -c "import slingshot; print('✓ Slingshot package loaded')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✅ Installation Complete!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green

    Write-Host "Quick Start Commands:`n" -ForegroundColor Cyan

    Write-Host "  Web UI (easiest):" -ForegroundColor Yellow
    Write-Host "    python webapp.py`n" -ForegroundColor White

    Write-Host "  Command Line:" -ForegroundColor Yellow
    Write-Host "    python -m slingshot themes" -ForegroundColor White
    Write-Host "    python -m slingshot scan --top 10" -ForegroundColor White
    Write-Host "    python -m slingshot ticker NVDA`n" -ForegroundColor White

    Write-Host "  Get Help:" -ForegroundColor Yellow
    Write-Host "    python -m slingshot --help`n" -ForegroundColor White

    Write-Host "Read QUICKSTART.md for detailed instructions!`n" -ForegroundColor Cyan

} else {
    Write-Host "`n✗ Installation test failed" -ForegroundColor Red
    Write-Host "Check for errors above" -ForegroundColor Yellow
}
