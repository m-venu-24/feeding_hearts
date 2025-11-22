# Feeding Hearts - Full Stack Application

A complete community food donation platform combining Django AI/ML, Laravel Web, Java high-performance services, MongoDB database, and Flutter mobile app.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend Layer                         │
│  ├─ Flutter Mobile App (iOS/Android)                   │
│  └─ Web Dashboard (React/Vue)                          │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│              API Gateway (Nginx)                        │
│  - Load Balancing                                       │
│  - SSL/TLS Termination                                 │
│  - Request Routing                                     │
└──┬──────────────┬──────────────────┬───────────────────┘
   │              │                  │
┌──▼──┐  ┌──────▼──┐  ┌───────────┴─────┐
│     │  │         │  │                 │
│ Django  │ Laravel │ │  Java Service  │
│ AI/ML   │ Web App │ │ (High-Perf)    │
│         │         │ │                 │
└────┬────┘  └───┬──┘  └────┬───────────┘
     │           │          │
     └───────┬───┴─────┬────┘
             │         │
         ┌───▼─────────▼───┐
         │   MongoDB       │
         │   PostgreSQL    │
         │   Redis Cache   │
         └─────────────────┘
```

## 🛠️ Technology Stack

### Backend Services

1. **Django (AI/ML Service)**
   - Machine learning models for donation prediction
   - Recommendation engine
   - Anomaly detection
   - Natural language processing

2. **Laravel (Web Application)**
   - RESTful API
   - Authentication & Authorization
   - Business logic
   - Admin panel

3. **Java (High-Performance Service)**
   - Geolocation calculations
   - Real-time processing
   - High-throughput operations
   - Microservices

### Databases

- **MongoDB**: Document storage for users, donations, requests
- **PostgreSQL**: Relational data (optional)
- **Redis**: Caching and message queue

### Frontend

- **Flutter**: Native mobile app (iOS/Android)
- **Web Dashboard**: React/Vue (to be implemented)

## 📋 Project Structure

```
feeding_hearts_fullstack/
├── backend/
│   ├── django-ai-ml/
│   │   ├── config/
│   │   ├── api/
│   │   ├── ml_models/
│   │   ├── predictions/
│   │   ├── analytics/
│   │   ├── manage.py
│   │   └── requirements.txt
│   │
│   ├── laravel-web/
│   │   ├── app/
│   │   │   ├── Http/Controllers/Api/
│   │   │   ├── Models/
│   │   │   └── Services/
│   │   ├── routes/api.php
│   │   ├── composer.json
│   │   └── .env.example
│   │
│   └── java-service/
│       ├── src/main/java/com/feedinghearts/
│       │   ├── api/
│       │   ├── service/
│       │   └── model/
│       ├── pom.xml
│       └── Dockerfile
│
├── frontend/
│   ├── flutter/
│   │   ├── lib/
│   │   │   ├── screens/
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── widgets/
│   │   └── pubspec.yaml
│   │
│   └── web/
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   └── services/
│       └── package.json
│
├── database/
│   └── mongodb/
│       ├── schema.js
│       └── migrations/
│
├── docker-compose.yml
├── nginx.conf
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+
- Java 17+
- Flutter 3.0+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/feeding_hearts_fullstack.git
cd feeding_hearts_fullstack
```

2. **Start all services with Docker**
```bash
docker-compose up -d
```

3. **Initialize MongoDB**
```bash
docker exec feeding_hearts_mongodb mongosh admin -u admin -p password < database/mongodb/schema.js
```

4. **Setup Django**
```bash
docker exec feeding_hearts_django python manage.py migrate
docker exec feeding_hearts_django python manage.py createsuperuser
```

5. **Setup Laravel**
```bash
docker exec feeding_hearts_laravel composer install
docker exec feeding_hearts_laravel cp .env.example .env
docker exec feeding_hearts_laravel php artisan key:generate
docker exec feeding_hearts_laravel php artisan migrate
```

### Services Running

- **Django**: http://localhost:8000
- **Laravel**: http://localhost:8001
- **Java**: http://localhost:8080
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

## 📚 API Documentation

### Django (AI/ML)
- `POST /api/token/` - Get JWT token
- `POST /api/users/register/` - Register user
- `POST /api/users/login/` - Login user
- `POST /api/ml/donation-demand/` - Predict donation demand
- `POST /api/ml/recommend/` - Get recommendations
- `POST /api/ml/anomaly/` - Detect anomalies

### Laravel (Web)
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/donations` - List donations
- `POST /api/donations` - Create donation
- `POST /api/donations/{id}/claim` - Claim donation
- `GET /api/requests` - List food requests
- `POST /api/requests` - Create request

### Java (Geolocation)
- `POST /api/geo/distance` - Calculate distance
- `POST /api/geo/nearby` - Find nearby donations
- `GET /api/geo/validate` - Validate coordinates

## 🔐 Security

- JWT authentication across all services
- MongoDB user validation
- API rate limiting
- CORS configuration
- SSL/TLS encryption
- Input validation and sanitization

## 📊 Database Schema

### Collections

1. **users** - User profiles and authentication
2. **donations** - Food donation listings
3. **food_requests** - Community food requests
4. **transactions** - Donation claims and completions
5. **reviews** - User ratings and reviews
6. **events** - Analytics events

## 🤖 ML Models

### Donation Predictor
- Predicts supply/demand patterns
- Uses RandomForest algorithm
- Features: location, time, category, history

### Recommendation Engine
- Collaborative filtering
- Suggests donations based on preferences
- K-nearest neighbors algorithm

### Anomaly Detector
- Identifies suspicious patterns
- Fraud detection
- Quality assurance

## 📱 Mobile App Features

- Real-time donation browsing
- Location-based matching
- User authentication
- Donation creation/claiming
- Request posting
- User profiles & ratings
- Push notifications
- Offline support

## 🌐 Web Dashboard Features

- Admin panel
- Analytics dashboard
- User management
- Donation verification
- Impact metrics
- Community insights

## 🧪 Testing

```bash
# Django tests
docker exec feeding_hearts_django python manage.py test

# Laravel tests
docker exec feeding_hearts_laravel php artisan test

# Java tests
docker exec feeding_hearts_java mvn test
```

## 📈 Performance Optimization

- Redis caching layer
- Database indexing
- Geolocation optimizations
- Asynchronous processing with Celery
- Load balancing with Nginx

## 🔄 Deployment

### Docker Production Setup
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment
- AWS ECS/EKS
- Google Cloud Run
- Azure Container Instances

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

- Issue Tracker: GitHub Issues
- Email: support@feedinghearts.app
- Documentation: Wiki

---

**Making food sharing accessible to everyone!** ❤️
