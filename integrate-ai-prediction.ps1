#!/usr/bin/env powershell
<#
.SYNOPSIS
    Automatic AI Prediction Integration Script for Feeding Hearts Project
    
.DESCRIPTION
    This script automatically integrates the AI Prediction System with the Feeding Hearts project.
    It handles:
    - Django settings configuration
    - Database setup and migrations
    - ML model initialization
    - Monitoring system setup
    - Alert configuration
    
.EXAMPLE
    .\integrate-ai-prediction.ps1
    .\integrate-ai-prediction.ps1 -SkipDB -SkipModels
    
.NOTES
    Requires Python 3.8+ and Django 4.2+
#>

param(
    [switch]$SkipDB = $false,
    [switch]$SkipModels = $false,
    [switch]$Test = $false,
    [switch]$NoVenv = $false
)

# Colors
$Success = @{ForegroundColor = "Green"}
$Warning = @{ForegroundColor = "Yellow"}
$Error = @{ForegroundColor = "Red"}
$Info = @{ForegroundColor = "Cyan"}

function Write-Step($Step, $Description) {
    Write-Host "`n" -NoNewline
    Write-Host ("="*70) -f Green
    Write-Host "STEP $Step : $Description" -f Green
    Write-Host ("="*70) -f Green
}

function Write-Success($Message) {
    Write-Host "✓ $Message" @Success
}

function Write-Warn($Message) {
    Write-Host "⚠ $Message" @Warning
}

function Write-Error-Custom($Message) {
    Write-Host "✗ $Message" @Error
}

function Write-Info($Message) {
    Write-Host "ℹ $Message" @Info
}

try {
    Write-Host "`n" @Success
    Write-Host ("="*70) @Success
    Write-Host "🚀 AUTOMATIC AI PREDICTION INTEGRATION" @Success
    Write-Host "   Feeding Hearts Project" @Success
    Write-Host ("="*70) @Success
    
    # Step 0: Check Python Environment
    Write-Step "0" "Checking Python Environment"
    
    if (-not $NoVenv) {
        $venvPath = "venv"
        if (Test-Path "$venvPath\Scripts\Activate.ps1") {
            Write-Success "Virtual environment found at $venvPath"
            & "$venvPath\Scripts\Activate.ps1"
            Write-Success "Virtual environment activated"
        } else {
            Write-Warn "Virtual environment not found at $venvPath"
            Write-Info "Creating virtual environment..."
            python -m venv venv
            & "venv\Scripts\Activate.ps1"
            Write-Success "Virtual environment created and activated"
        }
    }
    
    # Verify Python
    $pythonVersion = python --version 2>&1
    Write-Success "Python found: $pythonVersion"
    
    # Step 1: Navigate to Django Project
    Write-Step "1" "Navigating to Django Project"
    
    $djangoDir = "backend\django-ai-ml"
    if (Test-Path $djangoDir) {
        Push-Location $djangoDir
        Write-Success "Changed to Django project directory"
    } else {
        Write-Error-Custom "Django directory not found at $djangoDir"
        exit 1
    }
    
    # Step 2: Install Dependencies
    Write-Step "2" "Verifying Dependencies"
    
    Write-Info "Checking required packages..."
    $packages = @("django", "djangorestframework", "scikit-learn", "tensorflow", "pandas")
    
    foreach ($package in $packages) {
        python -c "import $package" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$package is installed"
        } else {
            Write-Warn "$package not installed"
        }
    }
    
    # Step 3: Run Django Setup Command
    Write-Step "3" "Running AI Integration Setup"
    
    $setupArgs = @("manage.py", "setup_ai_integration")
    if ($SkipDB) { $setupArgs += "--skip-db" }
    if ($SkipModels) { $setupArgs += "--skip-models" }
    if ($Test) { $setupArgs += "--test" }
    
    Write-Info "Running: python $(($setupArgs) -join ' ')"
    python $setupArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Django setup command completed successfully"
    } else {
        Write-Error-Custom "Django setup command failed"
        exit 1
    }
    
    # Step 4: Run Python Integration Script
    Write-Step "4" "Running Python Integration Script"
    
    if (Test-Path "integrate_ai_prediction.py") {
        Write-Info "Running integrate_ai_prediction.py..."
        python integrate_ai_prediction.py
        Write-Success "Python integration script completed"
    } else {
        Write-Warn "integrate_ai_prediction.py not found in current directory"
    }
    
    # Step 5: Verify Configuration Files
    Write-Step "5" "Verifying Configuration Files"
    
    $configFiles = @(
        "config\ai_integration_settings.py",
        "config\settings.py",
        ".env"
    )
    
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Write-Success "Configuration file found: $file"
        } else {
            Write-Warn "Configuration file not found: $file"
        }
    }
    
    # Step 6: Database Migrations (if not skipped)
    if (-not $SkipDB) {
        Write-Step "6" "Running Database Migrations"
        
        Write-Info "Running: python manage.py migrate"
        python manage.py migrate
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database migrations completed"
        } else {
            Write-Warn "Database migrations had issues (database may not be running)"
        }
    } else {
        Write-Step "6" "Skipping Database Migrations"
        Write-Info "Database migrations skipped per user request"
    }
    
    # Step 7: Initialize Models (if not skipped)
    if (-not $SkipModels) {
        Write-Step "7" "Initializing ML Models"
        
        Write-Info "Initializing ML models..."
        python manage.py shell <<'PYTHON'
from ml_prediction.services import ErrorPredictionService
try:
    service = ErrorPredictionService()
    service.initialize_models()
    print("ML models initialized successfully")
except Exception as e:
    print(f"Warning: {str(e)}")
PYTHON
        
    } else {
        Write-Step "7" "Skipping ML Model Initialization"
        Write-Info "ML model initialization skipped per user request"
    }
    
    # Step 8: Test Integration (if requested)
    if ($Test) {
        Write-Step "8" "Running Integration Tests"
        
        Write-Info "Running Django tests..."
        python manage.py test ml_prediction error_logging
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "All tests passed"
        } else {
            Write-Warn "Some tests failed"
        }
    }
    
    # Final Summary
    Write-Host "`n" -NoNewline
    Write-Host ("="*70) -f Green
    Write-Host "✅ INTEGRATION SETUP COMPLETE" -f Green
    Write-Host ("="*70) -f Green
    
    Write-Host "`nNEXT STEPS:" -f Cyan
    Write-Host "-" -NoNewline -f Green
    Write-Host ("-"*69) -f Green
    
    $nextSteps = @(
        "1. Start the development server:",
        "   python manage.py runserver",
        "",
        "2. In another terminal, start Celery worker:",
        "   celery -A config worker -l info",
        "",
        "3. Test the integration:",
        "   python manage.py shell",
        "   >>> from error_logging.services import ErrorAlertManager",
        "   >>> manager = ErrorAlertManager()",
        "   >>> manager.test_alert()",
        "",
        "4. View the AI dashboard:",
        "   http://localhost:8000/api/ai-dashboard/",
        "",
        "5. Read the integration guide:",
        "   ../AI_INTEGRATION_GUIDE.md"
    )
    
    foreach ($step in $nextSteps) {
        Write-Host $step
    }
    
    Write-Host "`n" -NoNewline
    Write-Host ("="*70) -f Green
    Write-Host "For detailed documentation, see:" -f Green
    Write-Host "  - AI_ERROR_RECOVERY_GUIDE.md" -f Green
    Write-Host "  - PHASE10_AI_PREDICTION_GUIDE.md" -f Green
    Write-Host "  - AI_INTEGRATION_GUIDE.md" -f Green
    Write-Host ("="*70 + "`n") -f Green
    
    Pop-Location
    exit 0
    
} catch {
    Write-Error-Custom "An error occurred: $_"
    exit 1
}
