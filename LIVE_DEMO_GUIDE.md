# 🎬 Feeding Hearts - Live Demo Guide

## 🚀 Quick Demo Start

### Step 1: Start All Services

**Option A: Double-click `START_HERE.bat`** (Easiest!)

**Option B: Run PowerShell script:**
```powershell
.\start-project.ps1
```

**Option C: Manual start (4 terminals):**
```powershell
# Terminal 1 - Django
cd backend/django-ai-ml
python manage.py runserver 0.0.0.0:8000

# Terminal 2 - React
cd frontend/react-app
npm run dev

# Terminal 3 - Angular
cd frontend/angular-admin
npm start

# Terminal 4 - Vue
cd frontend/vue-integration
npm run dev
```

---

## 🎯 Live Demo URLs

Once services are running, access:

| Application | URL | What to Demo |
|------------|-----|--------------|
| **🎨 React App** | http://localhost:5173 | **Main Demo - Start Here!** |
| **🎯 Angular Admin** | http://localhost:4200 | Admin Dashboard |
| **⚡ Vue Integration** | http://localhost:5174 | Integration Dashboard |
| **🔧 Django API** | http://localhost:8000/api | Backend API |
| **🤖 AI Demo** | Run `python demo_ai_prediction_system.py` | AI Features |

---

## 📋 Demo Walkthrough

### Demo 1: React Consumer App (Main Demo)

**URL:** http://localhost:5173

#### Step 1: Homepage
- ✅ View the landing page
- ✅ See featured donations
- ✅ Browse available food items

#### Step 2: User Registration
1. Click "Sign Up" or "Register"
2. Fill in:
   - Name
   - Email
   - Password
3. Submit registration
4. **Result:** User account created, JWT token received

#### Step 3: Login
1. Enter email and password
2. Click "Login"
3. **Result:** Redirected to dashboard with JWT token

#### Step 4: Browse Donations
1. View donation cards
2. See donation details:
   - Food type
   - Quantity
   - Location
   - Expiration time
   - Donor information
3. Filter by category
4. Search donations

#### Step 5: Search Nearby Donations
1. Click "Find Nearby" or "Map View"
2. Allow location access
3. **Result:** See donations sorted by distance
4. View on map (if map integration available)

#### Step 6: Create Donation
1. Click "Donate Food" or "Create Donation"
2. Fill in form:
   - Food type
   - Description
   - Quantity
   - Location (or use GPS)
   - Dietary tags (vegetarian, vegan, etc.)
3. Upload photos (optional)
4. Submit
5. **Result:** Donation created and visible to others

#### Step 7: Claim Donation
1. Browse available donations
2. Click on a donation
3. Click "Claim" button
4. **Result:** Donation status changes to "claimed"
5. Contact donor for pickup

#### Step 8: View Analytics
1. Go to "Dashboard" or "My Impact"
2. See statistics:
   - Donations made
   - Donations claimed
   - Food saved (kg/lbs)
   - Lives helped
   - Community impact

---

### Demo 2: Angular Admin Dashboard

**URL:** http://localhost:4200

#### Features to Show:
1. **Admin Login**
   - Login with admin credentials
   - Access admin panel

2. **Dashboard Overview**
   - Total donations
   - Active users
   - Recent activity
   - Charts and graphs

3. **User Management**
   - View all users
   - User profiles
   - Verification status

4. **Donation Management**
   - View all donations
   - Filter by status
   - Approve/reject donations
   - Monitor claims

5. **Analytics**
   - Impact metrics
   - Trends analysis
   - Geographic distribution
   - Performance metrics

6. **Reports**
   - Generate reports
   - Export data
   - View statistics

---

### Demo 3: Vue Integration Dashboard

**URL:** http://localhost:5174

#### Features to Show:
1. **Real-time Updates**
   - Live donation feed
   - Real-time notifications

2. **Integration Features**
   - API integration status
   - Service health
   - Data synchronization

3. **Advanced Analytics**
   - Interactive charts
   - Data visualization
   - Custom reports

---

### Demo 4: Backend API Testing

**URL:** http://localhost:8000/api

#### Test Endpoints:

**1. Health Check:**
```bash
GET http://localhost:8000/api/health
```

**2. User Registration:**
```bash
POST http://localhost:8000/api/users/register/
Body: {
  "email": "demo@example.com",
  "password": "demo123",
  "name": "Demo User"
}
```

**3. User Login:**
```bash
POST http://localhost:8000/api/users/login/
Body: {
  "email": "demo@example.com",
  "password": "demo123"
}
Response: { "access": "...", "refresh": "..." }
```

**4. Get Donations:**
```bash
GET http://localhost:8000/api/donations/
Headers: Authorization: Bearer <token>
```

**5. Create Donation:**
```bash
POST http://localhost:8000/api/donations/
Headers: Authorization: Bearer <token>
Body: {
  "food_type": "Fresh Vegetables",
  "description": "Organic vegetables",
  "quantity": 10,
  "unit": "kg",
  "location": "123 Main St",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**6. Get Nearby Donations:**
```bash
GET http://localhost:8000/api/donations/nearby/?latitude=40.7128&longitude=-74.0060&radius=5
```

**7. AI Recommendations:**
```bash
POST http://localhost:8000/api/ml/recommend/
Body: {
  "user_id": "123",
  "location": {"lat": 40.7128, "lng": -74.0060}
}
```

**8. AI Demand Prediction:**
```bash
POST http://localhost:8000/api/ml/donation-demand/
Body: {
  "location": {"lat": 40.7128, "lng": -74.0060},
  "date": "2024-01-15"
}
```

---

### Demo 5: AI/ML Features Demo

**Run the AI Demo Script:**
```powershell
python demo_ai_prediction_system.py
```

#### What It Shows:
1. **Error Prediction**
   - Predicts potential system errors
   - Confidence scores
   - Preventive recommendations

2. **Anomaly Detection**
   - Detects unusual patterns
   - Fraud detection
   - Quality assurance

3. **Time Series Forecasting**
   - Predicts donation demand
   - Capacity planning
   - Trend analysis

4. **Root Cause Analysis**
   - Analyzes error causes
   - Provides insights
   - Suggests solutions

---

## 🎬 Complete Demo Script

### 5-Minute Quick Demo

1. **Start Services** (30 seconds)
   - Run `START_HERE.bat`
   - Wait for services to start

2. **Open React App** (1 minute)
   - Go to http://localhost:5173
   - Show homepage
   - Register new user
   - Login

3. **Create Donation** (1 minute)
   - Click "Donate Food"
   - Fill form
   - Submit
   - Show in list

4. **Search & Claim** (1 minute)
   - Search nearby donations
   - View on map
   - Claim a donation
   - Show status change

5. **View Analytics** (1 minute)
   - Go to dashboard
   - Show impact metrics
   - Show charts
   - Show trends

6. **AI Features** (30 seconds)
   - Show recommendations
   - Show demand prediction
   - Show anomaly detection

---

## 🎥 Demo Checklist

### Before Demo:
- [ ] All services running
- [ ] Database connected
- [ ] Test user created
- [ ] Sample donations added
- [ ] Browser ready

### During Demo:
- [ ] Show React app homepage
- [ ] Register/Login user
- [ ] Create donation
- [ ] Browse donations
- [ ] Search nearby
- [ ] Claim donation
- [ ] View analytics
- [ ] Show AI features
- [ ] Show admin dashboard

### After Demo:
- [ ] Answer questions
- [ ] Show code structure
- [ ] Explain architecture
- [ ] Discuss features

---

## 🛠️ Troubleshooting Demo

### Services Not Starting?
```powershell
# Check if ports are in use
netstat -ano | findstr ":5173 :8000 :4200"

# Kill process if needed
taskkill /PID <process_id> /F
```

### Database Errors?
```powershell
# Django migrations
cd backend/django-ai-ml
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Frontend Not Loading?
```powershell
# Install dependencies
cd frontend/react-app
npm install

# Clear cache
npm run build
```

---

## 📸 Screenshots to Capture

1. **Homepage** - Landing page
2. **Registration** - Sign up form
3. **Dashboard** - User dashboard
4. **Donation List** - Browse donations
5. **Create Donation** - Donation form
6. **Map View** - Nearby donations
7. **Analytics** - Impact metrics
8. **Admin Panel** - Admin dashboard
9. **AI Recommendations** - ML suggestions

---

## 🎯 Key Features to Highlight

1. **Real-time Updates** - Live donation feed
2. **Location-based Matching** - Nearby search
3. **AI Recommendations** - Smart suggestions
4. **Impact Tracking** - Analytics dashboard
5. **Multi-platform** - React, Angular, Vue
6. **Secure Authentication** - JWT tokens
7. **Scalable Architecture** - Microservices
8. **Error Recovery** - Auto-healing system

---

## 🚀 Ready to Demo!

**Start here:** http://localhost:5173

**Have fun showcasing Feeding Hearts! 🎉**

