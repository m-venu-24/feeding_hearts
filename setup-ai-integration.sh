#!/bin/bash
# Automatic AI Prediction Integration Setup Script for Feeding Hearts
# Usage: bash setup-ai-integration.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${GREEN}========================================================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================================================${NC}\n"
}

print_step() {
    echo -e "\n${BLUE}STEP $1: $2${NC}"
    echo -e "${BLUE}$(printf '%.0s-' {1..70})${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Main Script
print_header "🚀 AUTOMATIC AI PREDICTION INTEGRATION"
print_header "   Feeding Hearts Project"

# Step 0: Check for Python
print_step "0" "Checking Python Environment"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

python_version=$(python3 --version 2>&1)
print_success "Found: $python_version"

# Step 1: Check Virtual Environment
print_step "1" "Checking Virtual Environment"

if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found, creating one..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate
print_success "Virtual environment activated"

# Step 2: Navigate to Django Directory
print_step "2" "Navigating to Django Project"

if [ ! -d "backend/django-ai-ml" ]; then
    print_error "Django project directory not found at backend/django-ai-ml"
    exit 1
fi

cd backend/django-ai-ml
print_success "Changed to Django project directory"

# Step 3: Install Dependencies
print_step "3" "Installing Dependencies"

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "requirements.txt not found"
fi

# Step 4: Check Configuration Files
print_step "4" "Checking Configuration Files"

if [ ! -f "config/settings.py" ]; then
    print_error "Django settings.py not found"
    exit 1
fi
print_success "Django settings.py found"

if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating template..."
    cat > .env << 'EOF'
# Database Configuration
DB_NAME=feeding_hearts
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# MongoDB Configuration
MONGO_DB=feeding_hearts_ml
MONGO_HOST=mongodb://localhost:27017

# Alert Configuration
ERROR_ALERT_RECIPIENTS=ops@feedinghearts.com

# Recovery Settings
AUTO_RECOVERY_ENABLED=True
RECOVERY_TIMEOUT=5

# Redis Configuration
REDIS_URL=redis://localhost:6379/1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EOF
    print_success ".env file created"
fi

# Step 5: Run Migrations
print_step "5" "Running Database Migrations"

print_warning "Checking database connection..."

if python3 manage.py migrate --plan > /dev/null 2>&1; then
    python3 manage.py migrate
    print_success "Database migrations completed"
else
    print_warning "Database not available (this is normal if PostgreSQL is not running)"
    print_warning "You can run migrations later with: python manage.py migrate"
fi

# Step 6: Run Django Setup Command
print_step "6" "Running AI Integration Setup"

if python3 manage.py setup_ai_integration 2>/dev/null; then
    print_success "Django setup command completed"
else
    print_warning "Django setup command not available"
    print_info "This is normal if management commands aren't set up yet"
fi

# Step 7: Run Python Integration Script
print_step "7" "Running Python Integration Script"

if [ -f "integrate_ai_prediction.py" ]; then
    python3 integrate_ai_prediction.py
    print_success "Python integration script completed"
else
    print_warning "Integration script not found"
fi

# Step 8: Verify Installation
print_step "8" "Verifying Installation"

# Check error_logging module
python3 << 'PYTHON'
import sys
try:
    from error_logging.models import ErrorLog
    print("✓ Error logging models available")
except ImportError:
    print("⚠ Error logging not fully available")

try:
    from ml_prediction.services import ErrorPredictionService
    print("✓ ML prediction services available")
except ImportError:
    print("⚠ ML prediction services not available")

try:
    from error_logging.ai_error_recovery import AutoRecoveryExecutor
    print("✓ Auto recovery executor available")
except ImportError:
    print("⚠ Auto recovery not available")
PYTHON

# Final Summary
print_header "✅ INTEGRATION SETUP COMPLETE"

echo -e "${BLUE}NEXT STEPS:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "2. In another terminal, start Celery worker (if using async tasks):"
echo "   celery -A config worker -l info"
echo ""
echo "3. Test the integration:"
echo "   python manage.py shell"
echo "   >>> from error_logging.services import ErrorAlertManager"
echo "   >>> manager = ErrorAlertManager()"
echo "   >>> manager.test_alert()"
echo ""
echo "4. View the AI dashboard:"
echo "   http://localhost:8000/api/ai-dashboard/"
echo ""
echo "5. Read the integration guide:"
echo "   ../AI_INTEGRATION_GUIDE.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For detailed documentation, see:"
echo "  - AI_ERROR_RECOVERY_GUIDE.md"
echo "  - PHASE10_AI_PREDICTION_GUIDE.md"
echo "  - AI_INTEGRATION_GUIDE.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Return to original directory
cd - > /dev/null

exit 0
