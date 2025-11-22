# 🌐 Feeding Hearts - Access URLs

## 🚀 Quick Start

### Option 1: Double-Click Startup (Easiest)
**Double-click:** `START_HERE.bat`

This will automatically start all services in separate windows.

---

### Option 2: PowerShell Script
```powershell
.\start-project.ps1
```

---

## 📍 Access URLs

Once services are running, open these URLs in your browser:

### Frontend Applications

| Application | URL | Description |
|------------|-----|-------------|
| 🎨 **React App** | http://localhost:5173 | Main consumer application |
| 🎯 **Angular Admin** | http://localhost:4200 | Admin dashboard |
| ⚡ **Vue Integration** | http://localhost:5174 | Integration dashboard |

### Backend APIs

| Service | URL | Description |
|--------|-----|-------------|
| 🔧 **Django API** | http://localhost:8000/api | Main backend API |
| 🔧 **Django Admin** | http://localhost:8000/admin | Django admin panel |
| 📊 **API Health** | http://localhost:8000/api/health | Health check |

---

## 🎯 Recommended Starting Point

**Start here:** http://localhost:5173 (React App)

This is the main consumer-facing application where you can:
- ✅ Register/Login
- ✅ Browse donations
- ✅ Create donations
- ✅ Claim donations
- ✅ Search nearby donations
- ✅ View analytics

---

## ⚠️ Important Notes

1. **Wait 10-30 seconds** after starting for all services to fully load
2. **Check the terminal windows** for any error messages
3. **First time?** You may need to install dependencies:
   ```powershell
   # Django
   cd backend/django-ai-ml
   pip install -r requirements.txt
   
   # React
   cd frontend/react-app
   npm install
   ```

---

## 🛑 Stopping Services

- Close the command prompt windows, OR
- Press `Ctrl+C` in each terminal window

---

## ✅ Verification

Test if services are running:

```powershell
# Test Django API
curl http://localhost:8000/api/

# Test React App
curl http://localhost:5173
```

Or simply open the URLs in your browser!

---

**Happy Browsing! 🎉**

