#!/usr/bin/env bash
# Project Structure Checker - Verify complete file tree

echo "🗂️  FEEDING HEARTS PROJECT STRUCTURE VERIFICATION"
echo "=================================================="
echo ""

# Define expected structure
declare -a REQUIRED_DIRS=(
    "backend/django-ai-ml"
    "backend/laravel-web"
    "backend/java-service"
    "frontend/angular-admin"
    "frontend/react-app"
    "frontend/vue-integration"
    "frontend/flutter"
    "frontend/styles"
    "frontend/nginx"
    "frontend/shared"
    "database/mongodb"
)

declare -a REQUIRED_FILES=(
    # Root
    "README.md"
    "ARCHITECTURE.md"
    "INTEGRATION.md"
    "API_REFERENCE.md"
    "docker-compose.yml"
    "docker-compose.full.yml"
    
    # Django
    "backend/django-ai-ml/requirements.txt"
    "backend/django-ai-ml/config/settings.py"
    "backend/django-ai-ml/config/urls.py"
    "backend/django-ai-ml/api/serializers.py"
    "backend/django-ai-ml/api/views.py"
    "backend/django-ai-ml/ml_models/models.py"
    "backend/django-ai-ml/ml_models/views.py"
    
    # Laravel
    "backend/laravel-web/composer.json"
    "backend/laravel-web/routes/api.php"
    "backend/laravel-web/app/Models/Donation.php"
    "backend/laravel-web/app/Http/Controllers/Api/DonationController.php"
    
    # Java
    "backend/java-service/pom.xml"
    "backend/java-service/src/main/java/com/feedinghearts/FeedingHeartsApplication.java"
    "backend/java-service/src/main/java/com/feedinghearts/model/Donation.java"
    "backend/java-service/src/main/java/com/feedinghearts/service/GeoLocationService.java"
    
    # Database
    "database/mongodb/schema.js"
    
    # Angular
    "frontend/angular-admin/package.json"
    "frontend/angular-admin/src/app/app.module.ts"
    "frontend/angular-admin/src/app/services/backend.service.ts"
    "frontend/angular-admin/src/app/guards/auth.guard.ts"
    "frontend/angular-admin/src/app/interceptors/auth.interceptor.ts"
    
    # React
    "frontend/react-app/package.json"
    "frontend/react-app/src/services/api.ts"
    "frontend/react-app/src/context/DonationContext.tsx"
    "frontend/react-app/src/components/DonationCard.tsx"
    "frontend/react-app/src/pages/HomePage.tsx"
    
    # Vue
    "frontend/vue-integration/package.json"
    "frontend/vue-integration/src/services/api.ts"
    "frontend/vue-integration/src/components/DonationDashboard.vue"
    "frontend/vue-integration/src/stores/donationStore.ts"
    
    # Frontend Shared
    "frontend/styles/global.css"
    "frontend/styles/README.md"
    "frontend/README.md"
    "frontend/nginx/nginx.conf"
    "frontend/shared/api-client.ts"
    
    # Flutter
    "frontend/flutter/pubspec.yaml"
    "frontend/flutter/lib/main.dart"
    "frontend/flutter/lib/models/user_model.dart"
    "frontend/flutter/lib/providers/user_provider.dart"
    "frontend/flutter/lib/providers/donation_provider.dart"
    "frontend/flutter/lib/screens/home_screen.dart"
)

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

missing_dirs=0
missing_files=0

echo "📁 Checking Directories..."
echo ""

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir"
    else
        echo -e "${RED}✗${NC} $dir (MISSING)"
        missing_dirs=$((missing_dirs + 1))
    fi
done

echo ""
echo "📄 Checking Files..."
echo ""

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file" 2>/dev/null | tr -d ' ')
        echo -e "${GREEN}✓${NC} $file ($(($size/1024))KB)"
    else
        echo -e "${RED}✗${NC} $file (MISSING)"
        missing_files=$((missing_files + 1))
    fi
done

echo ""
echo "📊 SUMMARY"
echo "=========="
total_dirs=${#REQUIRED_DIRS[@]}
total_files=${#REQUIRED_FILES[@]}
present_dirs=$((total_dirs - missing_dirs))
present_files=$((total_files - missing_files))

echo "Directories: $present_dirs/$total_dirs"
echo "Files:       $present_files/$total_files"
echo ""

if [ "$missing_dirs" -eq 0 ] && [ "$missing_files" -eq 0 ]; then
    echo -e "${GREEN}✓ ALL FILES PRESENT!${NC}"
    exit 0
else
    echo -e "${RED}✗ MISSING FILES/DIRECTORIES${NC}"
    [ "$missing_dirs" -gt 0 ] && echo "  - Missing directories: $missing_dirs"
    [ "$missing_files" -gt 0 ] && echo "  - Missing files: $missing_files"
    exit 1
fi
