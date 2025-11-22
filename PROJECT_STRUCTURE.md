FEEDING_HEARTS_FULLSTACK/
├── backend/
│   ├── django-ai-ml/              # AI/ML Services
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   ├── config/
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   └── wsgi.py
│   │   ├── apps/
│   │   │   ├── api/
│   │   │   ├── ml_models/
│   │   │   ├── predictions/
│   │   │   └── analytics/
│   │   └── models/
│   │       ├── donation_predictor.pkl
│   │       └── recommendation_engine.pkl
│   │
│   ├── laravel-web/               # Laravel Web Application
│   │   ├── app/
│   │   │   ├── Http/
│   │   │   │   ├── Controllers/
│   │   │   │   └── Middleware/
│   │   │   ├── Models/
│   │   │   └── Services/
│   │   ├── routes/
│   │   │   ├── api.php
│   │   │   └── web.php
│   │   ├── database/
│   │   │   └── migrations/
│   │   ├── resources/
│   │   │   └── views/
│   │   └── .env.example
│   │
│   └── java-service/              # Java High-Performance Service
│       ├── src/
│       │   ├── main/
│       │   │   ├── java/
│       │   │   │   └── com/feedinghearts/
│       │   │   │       ├── api/
│       │   │   │       ├── service/
│       │   │   │       └── model/
│       │   │   └── resources/
│       │   └── test/
│       ├── pom.xml
│       └── Dockerfile
│
├── frontend/
│   ├── flutter/                   # Mobile App (already created)
│   └── web/                       # Web Dashboard
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── services/
│       │   └── App.jsx
│       ├── package.json
│       └── vite.config.js
│
├── database/
│   ├── mongodb/
│   │   ├── schemas/
│   │   │   ├── user.schema.js
│   │   │   ├── donation.schema.js
│   │   │   ├── request.schema.js
│   │   │   └── transaction.schema.js
│   │   ├── migrations/
│   │   └── init-db.js
│   └── indexes.js
│
├── docker-compose.yml
├── README.md
└── ARCHITECTURE.md