# 🚀 How to Run Feeding Hearts Project

## Quick Start Guide

### Option 1: Using PowerShell Script (Recommended)

Run the startup script:
```powershell
.\start-project.ps1
```

This will automatically start all services in separate windows.

---

### Option 2: Manual Startup

#### Step 1: Install Dependencies (First Time Only)

**Django Backend:**
```powershell
cd backend/django-ai-ml
python -m pip install -r requirements.txt
```

**React Frontend:**
```powershell
cd frontend/react-app
npm install
```

**Angular Frontend:**
```powershell
cd frontend/angular-admin
npm install
```

**Vue Frontend:**
```powershell
cd frontend/vue-integration
npm install
```

---

#### Step 2: Start Services

**Terminal 1 - Django Backend:**
```powershell
cd backend/django-ai-ml
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
**URL:** http://localhost:8000

---

**Terminal 2 - React App:**
```powershell
cd frontend/react-app
npm run dev
```
**URL:** http://localhost:5173

---

**Terminal 3 - Angular Admin:**
```powershell
cd frontend/angular-admin
npm start
```
**URL:** http://localhost:4200

---

**Terminal 4 - Vue Integration:**
```powershell
cd frontend/vue-integration
npm run dev
```
**URL:** http://localhost:5174

---

## 🌐 Access URLs

Once all services are running, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| **React App** | http://localhost:5173 | Consumer-facing application |
| **Angular Admin** | http://localhost:4200 | Admin dashboard |
| **Vue Integration** | http://localhost:5174 | Integration dashboard |
| **Django API** | http://localhost:8000/api | Backend API |
| **Django Admin** | http://localhost:8000/admin | Django admin panel |

---

## ⚠️ Important Notes

### Database Setup

Before running Django, you need to:

1. **Set up MongoDB** (if using):
   - Install MongoDB locally, OR
   - Use MongoDB Atlas (cloud), OR
   - Use Docker: `docker run -d -p 27017:27017 mongo:7.0`

2. **Set up PostgreSQL** (if using):
   - Install PostgreSQL locally, OR
   - Use Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:16`

3. **Run Django Migrations:**
   ```powershell
   cd backend/django-ai-ml
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Environment Variables

Create `.env` files if needed:

**Django:** `backend/django-ai-ml/.env`
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

**React:** `frontend/react-app/.env.development`
```env
VITE_API_URL=http://localhost:8000/api
```

---

## 🐳 Using Docker (If Installed)

If you have Docker installed:

```powershell
docker-compose up -d
```

This starts all services automatically:
- MongoDB (port 27017)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Django (port 8000)
- Laravel (port 8001)
- Java (port 8080)
- Nginx (port 80)

---

## 🛑 Stopping Services

- **PowerShell Script:** Close the PowerShell windows
- **Manual:** Press `Ctrl+C` in each terminal
- **Docker:** `docker-compose down`

---

## ✅ Verification

Check if services are running:

```powershell
# Check Django
curl http://localhost:8000/api/

# Check React
curl http://localhost:5173

# Check Angular
curl http://localhost:4200
```

---

## 🆘 Troubleshooting

### Port Already in Use
If a port is already in use:
- Change the port in the service configuration
- Or stop the service using that port

### Dependencies Not Found
```powershell
# Python packages
pip install -r backend/django-ai-ml/requirements.txt

# Node packages
cd frontend/react-app && npm install
cd frontend/angular-admin && npm install
cd frontend/vue-integration && npm install
```

### Database Connection Error
- Make sure MongoDB/PostgreSQL is running
- Check connection strings in settings
- Verify database credentials

---

## 📝 Next Steps

1. **Access the React App:** http://localhost:5173
2. **Register a new user** or login
3. **Create a donation** or browse existing ones
4. **Test the features:**
   - Search nearby donations
   - Claim donations
   - View analytics
   - Use AI recommendations

---

**Happy Coding! 🎉**

