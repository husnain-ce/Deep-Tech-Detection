# Ultimate Web Technology Detection System PowerShell Launcher

Write-Host "🚀 Ultimate Web Technology Detection System" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is required but not installed" -ForegroundColor Red
    exit 1
}

# Run the detector
python main.py $args
