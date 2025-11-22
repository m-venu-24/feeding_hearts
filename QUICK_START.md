# Quick Start Guide - Feeding Hearts Project

## Prerequisites

### Option 1: Using Docker (Recommended)
1. **Install Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer
   - Make sure Docker Desktop is running

2. **Verify Docker Installation**
   ```powershell
   docker --version
   docker-compose --version
   ```

### Option 2: Run Services Manually (Without Docker)
You'll need:
- Python 3.10+ (for Django)
- PHP 8.2+ and Composer (for Laravel)
- Java 17+ and Maven (for Java service)
- MongoDB (running locally)
- PostgreSQL (running locally)
- Redis (running locally)
- Node.js 18+ (for frontend)

## Running with Docker (Recommended)

### Step 1: Start All Services
```powershell
docker-compose up -d
```

This will start:
- MongoDB (port 27017)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Django API (port 8000)
- Laravel API (port 8001)
- Java Service (port 8080)
- Nginx Proxy (port 80)

### Step 2: Initialize Databases

**MongoDB:**
```powershell
docker exec feeding_hearts_mongodb mongosh -u admin -p password --authenticationDatabase admin feeding_hearts --eval "load('/docker-entrypoint-initdb.d/schema.js')"
```

**Django Migrations:**
```powershell
docker exec feeding_hearts_django python manage.py migrate
docker exec feeding_hearts_django python manage.py createsuperuser
```

**Laravel Setup:**
```powershell
docker exec feeding_hearts_laravel composer install
docker exec feeding_hearts_laravel php artisan key:generate
```

### Step 3: Verify Services

Check if all services are running:
```powershell
docker-compose ps
```

Test endpoints:
- Django: http://localhost:8000
- Laravel: http://localhost:8001
- Java: http://localhost:8080
- Nginx: http://localhost

### Step 4: View Logs

View logs for all services:
```powershell
docker-compose logs -f
```

View logs for specific service:
```powershell
docker-compose logs -f django
docker-compose logs -f laravel
docker-compose logs -f java
```

## Running Frontend Applications

### React App
```powershell
cd frontend/react-app
npm install
npm run dev
```
Access at: http://localhost:5173

### Angular Admin
```powershell
cd frontend/angular-admin
npm install
npm start
```
Access at: http://localhost:4200

### Vue Integration
```powershell
cd frontend/vue-integration
npm install
npm run dev
```
Access at: http://localhost:5174

## Troubleshooting

### Port Already in Use
If a port is already in use, you can:
1. Stop the service using that port
2. Change the port in `docker-compose.yml`

### Services Not Starting
1. Check Docker Desktop is running
2. Check logs: `docker-compose logs [service-name]`
3. Verify all Dockerfiles exist

### Database Connection Issues
1. Wait for databases to be fully initialized (30-60 seconds)
2. Check database health: `docker-compose ps`
3. Verify environment variables in docker-compose.yml

## Stopping Services

Stop all services:
```powershell
docker-compose down
```

Stop and remove volumes (clears data):
```powershell
docker-compose down -v
```

## Next Steps

1. Read `README.md` for project overview
2. Check `API_REFERENCE.md` for API documentation
3. Review `ARCHITECTURE.md` for system design
4. Run tests: `bash run-all-tests.sh` (if on Linux/WSL)

