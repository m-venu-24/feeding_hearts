# Quick Test Reference Card

## One-Command Test Everything
```bash
bash run-all-tests.sh
```

---

## Individual Test Categories

### Project Validation (No Dependencies)
```bash
# Check directory structure
bash check-structure.sh

# Validate all configurations
bash validate-project.sh
```

**Expected:** Instant results, no services needed

---

### Docker Infrastructure Tests
```bash
bash docker-health-check.sh
```

**Requirements:** Docker, Docker Compose, services running
**Duration:** ~2-3 minutes

---

### Backend Tests

#### Django (Python)
```bash
cd backend/django-ai-ml
pytest tests/test_api.py -v                    # Verbose output
pytest tests/test_api.py --cov=api             # With coverage
pytest tests/test_api.py::TestAuthAPI -v       # Specific class
pytest tests/test_api.py -k "test_login" -v    # Specific test
```

**Requirements:** Python 3.10+, pytest, Django dependencies
**Duration:** ~30-60 seconds

---

### Frontend Tests

#### React
```bash
cd frontend/react-app
npm test                                       # Watch mode
npm test -- --watchAll=false                   # Single run
npm test -- --coverage                         # With coverage
npm test -- --testNamePattern="api" --watch=false
```

**Requirements:** Node.js 18+, npm dependencies
**Duration:** ~1-2 minutes

#### Angular
```bash
cd frontend/angular-admin
ng test                                        # Watch mode
ng test --watch=false                          # Single run
ng test --code-coverage                        # With coverage
ng test --watch=false --browsers=ChromeHeadless
```

**Requirements:** Node.js 18+, Angular CLI, dependencies
**Duration:** ~1-2 minutes

#### Vue
```bash
cd frontend/vue-integration
npm run test:unit                              # Run tests
npm run test:unit:ui                           # UI dashboard
npm run test:unit -- --coverage                # With coverage
npm run test:unit -- --reporter=verbose
```

**Requirements:** Node.js 18+, Vitest, dependencies
**Duration:** ~1-2 minutes

---

### E2E Integration Tests
```bash
bash e2e-integration-test.sh
```

**Requirements:** Backend services running, API accessible
**Duration:** ~3-5 minutes
**Tests:** 50+ test cases covering full user workflows

---

## Test Output Examples

### ✓ All Passing
```
═══════════════════════════════════════════════════════════
COMPREHENSIVE TEST SUITE RUNNER
═══════════════════════════════════════════════════════════

► PHASE 1: Project Structure Validation
✓ Project Structure Check PASSED

► PHASE 2: Project Validation
✓ Project Validation PASSED

► PHASE 3: Docker Infrastructure Tests
✓ Docker Health Check PASSED

► PHASE 4: Backend Unit Tests
✓ Django API Tests PASSED

► PHASE 5: Frontend Unit Tests
✓ React API Tests PASSED
✓ Angular Service Tests PASSED
✓ Vue Store Tests PASSED

► PHASE 6: E2E Integration Tests
✓ E2E Full Workflow Tests PASSED

═══════════════════════════════════════════════════════════
TEST SUMMARY
═══════════════════════════════════════════════════════════
Total Test Suites:      6
Passed:                 6
Failed:                 0
Success Rate:           100%
Duration:              5m 45s

╔═══════════════════════════════════════════════════════════╗
║ ✓ ALL TEST SUITES PASSED - SYSTEM READY FOR DEPLOYMENT   ║
╚═══════════════════════════════════════════════════════════╝
```

### ⚠ With Warnings
```
═══════════════════════════════════════════════════════════
TEST SUMMARY
═══════════════════════════════════════════════════════════
Total Test Suites:      5
Passed:                 4
Failed:                 1
Success Rate:           80%
Duration:              4m 20s

⚠ docker-health-check.sh not found, skipping

✗ Docker Health Check FAILED
  → java-service failed to become healthy within 60s
  → Check: docker-compose logs java-service
```

---

## Environment Setup

### One-Time Setup
```bash
# Backend dependencies
cd backend/django-ai-ml && pip install -r requirements.txt
cd backend/laravel-web && composer install
cd backend/java-service && mvn clean install

# Frontend dependencies
cd frontend/react-app && npm install
cd frontend/angular-admin && npm install
cd frontend/vue-integration && npm install
cd frontend && npm install

# Copy environment files
cp .env.example .env
cp backend/django-ai-ml/.env.example backend/django-ai-ml/.env
cp backend/laravel-web/.env.example backend/laravel-web/.env
```

### Start Services
```bash
# Docker services
docker-compose -f docker-compose.full.yml up -d

# Or individual services
cd backend/django-ai-ml && python manage.py runserver
cd backend/laravel-web && php artisan serve
```

---

## Common Issues & Solutions

### "Command not found"
```bash
# Make scripts executable
chmod +x *.sh
chmod +x backend/*/tests/*.sh
chmod +x e2e-*.sh
```

### "Port already in use"
```bash
# Find and kill process
lsof -i :8000  # Django
lsof -i :8001  # Laravel
lsof -i :8080  # Java

# Kill by PID
kill -9 <PID>
```

### "Database connection refused"
```bash
# Ensure services are running
docker-compose -f docker-compose.full.yml ps

# Restart database
docker-compose -f docker-compose.full.yml restart mongodb postgres
```

### "Module not found"
```bash
# Python
pip install -r requirements.txt
pip install -r requirements-test.txt  # Test dependencies

# Node
npm install
npm ci  # Cleaner install
```

### "CORS errors"
```bash
# Check Nginx configuration
docker exec nginx nginx -t

# View Nginx logs
docker logs nginx

# Restart Nginx
docker-compose -f docker-compose.full.yml restart nginx
```

---

## Debugging Tests

### Verbose Output
```bash
# Pytest
pytest -vv --tb=long

# Jest
npm test -- --verbose

# Vitest
npm run test:unit -- --reporter=verbose
```

### Run Single Test
```bash
# Django
pytest tests/test_api.py::TestAuthAPI::test_login -vv

# Jest
npm test -- --testNamePattern="test_login"

# Vitest
npm run test:unit -- --reporter=verbose tests/stores.test.ts
```

### Debug Mode
```bash
# Python
pytest --pdb tests/test_api.py

# Node (Chrome DevTools)
node --inspect-brk node_modules/.bin/jest --runInBand
```

### View Test Coverage
```bash
# Open HTML report
open htmlcov/index.html              # Python
open coverage/lcov-report/index.html # JavaScript
```

---

## Performance Tips

### Faster Tests
```bash
# Run tests in parallel
pytest -n auto                        # Python (pytest-xdist)

# Skip slow tests
pytest -m "not slow"

# Run only changed tests
pytest --lf                           # Last failed
pytest --ff                           # Failed first
```

### Faster Setup
```bash
# Use test database fixtures
pytest --fixtures

# Mock external services
# See test files for mock examples

# Reuse test data
# Use factories instead of creating fresh data
```

---

## Integration with IDE

### VS Code Configuration
Create `.vscode/settings.json`:
```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["backend/django-ai-ml/tests"],
  "jest.autoRun": "off",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### Run Tests in IDE
- **VS Code:** Click "Test" icon in sidebar
- **PyCharm:** Right-click test file → "Run pytest"
- **WebStorm:** Right-click test file → "Run Tests"

---

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run All Tests
  run: bash run-all-tests.sh

- name: Upload Coverage
  uses: codecov/codecov-action@v2
  with:
    files: ./coverage/coverage-final.json
```

### GitLab CI
```yaml
test:
  script:
    - bash run-all-tests.sh
  coverage: '/Coverage: \d+.\d+/'
```

---

## Success Checklist

Before deploying, ensure:
- [ ] `bash check-structure.sh` passes
- [ ] `bash validate-project.sh` passes
- [ ] `bash docker-health-check.sh` passes
- [ ] All unit tests pass (Django, React, Angular, Vue)
- [ ] E2E tests pass: `bash e2e-integration-test.sh`
- [ ] No coverage regression
- [ ] All CI/CD checks pass
- [ ] Documentation updated

---

**Quick Links:**
- Full Guide: See `TESTING.md`
- Architecture: See `ARCHITECTURE.md`
- Setup: Run `bash setup.sh`
- API Docs: See `API_REFERENCE.md`

**Contact:** Development Team
