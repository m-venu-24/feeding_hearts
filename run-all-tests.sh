#!/bin/bash

# Comprehensive Test Runner
# Executes all unit tests, integration tests, and validation scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0
START_TIME=$(date +%s)

# Configuration
COMPOSE_FILE="docker-compose.full.yml"
SKIP_DOCKER=${SKIP_DOCKER:-false}
SKIP_UNIT_TESTS=${SKIP_UNIT_TESTS:-false}
SKIP_E2E=${SKIP_E2E:-false}

# Helper functions
print_banner() {
  echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${MAGENTA}║${NC}  $1"
  echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
  echo ""
}

print_section() {
  echo -e "${CYAN}► $1${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

run_test_suite() {
  local suite_name=$1
  local test_command=$2
  local test_dir=${3:-.}
  
  TOTAL_SUITES=$((TOTAL_SUITES + 1))
  
  echo -e "${BLUE}[${TOTAL_SUITES}] Running: $suite_name${NC}"
  echo "Command: $test_command"
  echo ""
  
  if ( cd "$test_dir" && eval "$test_command" ); then
    echo -e "${GREEN}✓ $suite_name PASSED${NC}"
    PASSED_SUITES=$((PASSED_SUITES + 1))
  else
    echo -e "${RED}✗ $suite_name FAILED${NC}"
    FAILED_SUITES=$((FAILED_SUITES + 1))
  fi
  
  echo ""
  echo "───────────────────────────────────────────────────────────────"
  echo ""
}

# Display usage information
usage() {
  cat << EOF
Usage: $0 [OPTIONS]

Options:
  --skip-docker         Skip Docker-based tests
  --skip-unit-tests     Skip unit tests
  --skip-e2e            Skip E2E integration tests
  --help                Display this help message

Environment Variables:
  SKIP_DOCKER=true      Skip Docker tests
  SKIP_UNIT_TESTS=true  Skip unit tests
  SKIP_E2E=true         Skip E2E tests

Examples:
  $0                            # Run all tests
  $0 --skip-docker              # Skip Docker health checks
  $0 --skip-unit-tests --skip-e2e  # Only run validation scripts
  
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-docker)
      SKIP_DOCKER=true
      shift
      ;;
    --skip-unit-tests)
      SKIP_UNIT_TESTS=true
      shift
      ;;
    --skip-e2e)
      SKIP_E2E=true
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

# Main execution
print_banner "COMPREHENSIVE TEST SUITE RUNNER"
echo -e "Started at: ${YELLOW}$(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "Skip Docker: ${YELLOW}$SKIP_DOCKER${NC}"
echo -e "Skip Unit Tests: ${YELLOW}$SKIP_UNIT_TESTS${NC}"
echo -e "Skip E2E Tests: ${YELLOW}$SKIP_E2E${NC}"
echo ""

# Test 1: Project Structure Validation
print_section "PHASE 1: Project Structure Validation"

if [ -f "check-structure.sh" ]; then
  run_test_suite "Project Structure Check" "bash check-structure.sh"
else
  echo -e "${YELLOW}⚠ check-structure.sh not found, skipping${NC}"
fi

# Test 2: Project Validation
print_section "PHASE 2: Project Validation"

if [ -f "validate-project.sh" ]; then
  run_test_suite "Project Validation" "bash validate-project.sh"
else
  echo -e "${YELLOW}⚠ validate-project.sh not found, skipping${NC}"
fi

# Test 3: Docker Health Checks
if [ "$SKIP_DOCKER" != "true" ]; then
  print_section "PHASE 3: Docker Infrastructure Tests"
  
  if [ -f "$COMPOSE_FILE" ]; then
    if [ -f "docker-health-check.sh" ]; then
      run_test_suite "Docker Health Check" "bash docker-health-check.sh"
    else
      echo -e "${YELLOW}⚠ docker-health-check.sh not found, skipping${NC}"
    fi
  else
    echo -e "${YELLOW}⚠ $COMPOSE_FILE not found, skipping Docker tests${NC}"
  fi
fi

# Test 4: Backend Unit Tests
if [ "$SKIP_UNIT_TESTS" != "true" ]; then
  print_section "PHASE 4: Backend Unit Tests"
  
  # Django Tests
  if [ -f "backend/django-ai-ml/tests/test_api.py" ]; then
    run_test_suite "Django API Tests" "python -m pytest backend/django-ai-ml/tests/test_api.py -v --tb=short"
  else
    echo -e "${YELLOW}⚠ Django test file not found${NC}"
  fi
  
  # Laravel Tests
  if [ -f "backend/laravel-web/tests/Feature/DonationTest.php" ]; then
    run_test_suite "Laravel Feature Tests" "cd backend/laravel-web && php artisan test tests/Feature/DonationTest.php"
  else
    echo -e "${YELLOW}⚠ Laravel test file not found${NC}"
  fi
fi

# Test 5: Frontend Unit Tests
if [ "$SKIP_UNIT_TESTS" != "true" ]; then
  print_section "PHASE 5: Frontend Unit Tests"
  
  # React Tests
  if [ -f "frontend/react-app/src/__tests__/api.test.ts" ]; then
    run_test_suite "React API Tests" "cd frontend/react-app && npm test -- --coverage --watchAll=false" "frontend/react-app"
  else
    echo -e "${YELLOW}⚠ React test file not found${NC}"
  fi
  
  # Angular Tests
  if [ -f "frontend/angular-admin/src/app/services/backend.service.spec.ts" ]; then
    run_test_suite "Angular Service Tests" "cd frontend/angular-admin && ng test --watch=false --code-coverage" "frontend/angular-admin"
  else
    echo -e "${YELLOW}⚠ Angular test file not found${NC}"
  fi
  
  # Vue Tests
  if [ -f "frontend/vue-integration/src/__tests__/stores.test.ts" ]; then
    run_test_suite "Vue Store Tests" "cd frontend/vue-integration && npm run test:unit" "frontend/vue-integration"
  else
    echo -e "${YELLOW}⚠ Vue test file not found${NC}"
  fi
fi

# Test 6: Integration Tests
if [ "$SKIP_E2E" != "true" ]; then
  print_section "PHASE 6: E2E Integration Tests"
  
  if [ -f "e2e-integration-test.sh" ]; then
    run_test_suite "E2E Full Workflow Tests" "bash e2e-integration-test.sh"
  else
    echo -e "${YELLOW}⚠ e2e-integration-test.sh not found, skipping${NC}"
  fi
fi

# Summary
print_section "TEST SUMMARY"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo -e "${YELLOW}Total Test Suites:${NC}     $TOTAL_SUITES"
echo -e "${GREEN}Passed:${NC}                 $PASSED_SUITES"
echo -e "${RED}Failed:${NC}                 $FAILED_SUITES"

if [ $TOTAL_SUITES -gt 0 ]; then
  PASS_RATE=$((PASSED_SUITES * 100 / TOTAL_SUITES))
  echo -e "${CYAN}Success Rate:${NC}          ${PASS_RATE}%"
fi

echo -e "${CYAN}Duration:${NC}              ${MINUTES}m ${SECONDS}s"
echo ""

# Final result
if [ $FAILED_SUITES -eq 0 ] && [ $TOTAL_SUITES -gt 0 ]; then
  print_banner "✓ ALL TEST SUITES PASSED - SYSTEM READY FOR DEPLOYMENT"
  exit 0
elif [ $TOTAL_SUITES -eq 0 ]; then
  echo -e "${YELLOW}⚠ No tests were run (check file paths and options)${NC}"
  exit 0
else
  print_banner "✗ SOME TEST SUITES FAILED - REVIEW ERRORS ABOVE"
  exit 1
fi
