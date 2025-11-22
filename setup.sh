#!/usr/bin/env bash
# Feeding Hearts Full Stack Setup Script

set -e

echo "🚀 Setting up Feeding Hearts Full Stack..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create directories if they don't exist
echo "📁 Creating directory structure..."
mkdir -p database/mongodb
mkdir -p frontend/{angular-admin,react-app,vue-integration,styles,nginx}
mkdir -p backend/{django-ai-ml,laravel-web,java-service}
echo "✅ Directories created"
echo ""

# Set up environment files
echo "📝 Setting up environment files..."

# Angular
cat > frontend/angular-admin/.env.development << 'EOF'
NG_APP_API_URL=http://localhost:8000/api
NG_APP_ENV=development
NG_APP_VERSION=1.0.0-dev
NG_APP_LOG_LEVEL=debug
EOF

cat > frontend/angular-admin/.env.production << 'EOF'
NG_APP_API_URL=https://api.feeding-hearts.com/api
NG_APP_ENV=production
NG_APP_VERSION=1.0.0
NG_APP_LOG_LEVEL=error
EOF

# React
cat > frontend/react-app/.env.development << 'EOF'
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Feeding Hearts Dev
VITE_ENABLE_DEVTOOLS=true
VITE_LOG_LEVEL=debug
EOF

cat > frontend/react-app/.env.production << 'EOF'
VITE_API_URL=https://api.feeding-hearts.com/api
VITE_APP_NAME=Feeding Hearts
VITE_ENABLE_DEVTOOLS=false
VITE_LOG_LEVEL=error
EOF

# Vue
cat > frontend/vue-integration/.env.development << 'EOF'
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Feeding Hearts Integration Dev
VITE_ENABLE_DEVTOOLS=true
EOF

cat > frontend/vue-integration/.env.production << 'EOF'
VITE_API_URL=https://api.feeding-hearts.com/api
VITE_APP_NAME=Feeding Hearts Integration
VITE_ENABLE_DEVTOOLS=false
EOF

# Django
cat > backend/django-ai-ml/.env << 'EOF'
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings
ALLOWED_HOSTS=localhost,127.0.0.1,django,feeding-hearts.local
DB_ENGINE=django.db.backends.postgresql
DB_NAME=feeding_hearts
DB_USER=feeding_hearts
DB_PASSWORD=secure_password
DB_HOST=postgres
DB_PORT=5432
MONGODB_URI=mongodb://admin:secure_password@mongodb:27017/feeding_hearts
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:4200,http://localhost:5173,http://localhost:5174
EOF

# Laravel
cat > backend/laravel-web/.env << 'EOF'
APP_NAME=FeedingHearts
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8001
DB_CONNECTION=mongodb
DB_HOST=mongodb
DB_PORT=27017
DB_DATABASE=feeding_hearts
DB_USERNAME=admin
DB_PASSWORD=secure_password
MONGODB_URI=mongodb://admin:secure_password@mongodb:27017/feeding_hearts
REDIS_HOST=redis
REDIS_PORT=6379
EOF

echo "✅ Environment files created"
echo ""

# Start services
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.full.yml up -d

echo ""
echo "✅ All services started!"
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo ""
echo "🏥 Checking service health..."
echo ""

services=(
  "mongodb:27017"
  "postgres:5432"
  "redis:6379"
  "django:8000"
  "laravel:8001"
  "java:8002"
)

for service in "${services[@]}"; do
  IFS=':' read -r name port <<< "$service"
  if timeout 5 bash -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
    echo "✅ $name is running on port $port"
  else
    echo "⚠️  $name may not be ready yet"
  fi
done

echo ""
echo "📍 Service URLs:"
echo "  - Angular Admin:       http://localhost:4200"
echo "  - React App:           http://localhost:5173"
echo "  - Vue Integration:     http://localhost:5174"
echo "  - Nginx Proxy:         http://localhost"
echo "  - Django API:          http://localhost:8000/api"
echo "  - Laravel API:         http://localhost:8001/api"
echo "  - Java API:            http://localhost:8002/api"
echo ""

echo "📚 Documentation:"
echo "  - Integration Guide:   INTEGRATION.md"
echo "  - Frontend Docs:       frontend/README.md"
echo "  - Backend Docs:        README.md"
echo ""

echo "🛑 To stop all services:"
echo "  docker-compose -f docker-compose.full.yml down"
echo ""

echo "📋 To view logs:"
echo "  docker-compose -f docker-compose.full.yml logs -f [service-name]"
echo ""

echo "✨ Setup complete! Happy coding!"
