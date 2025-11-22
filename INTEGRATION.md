# Frontend-Backend Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
├──────────────────┬──────────────────┬───────────────────────┤
│  Angular Admin   │   React App      │  Vue Integration      │
│  (4200)          │   (5173)         │  (5174)               │
│  - Dashboard     │   - Home         │  - Real-time          │
│  - Analytics     │   - Donations    │  - Metrics            │
│  - Moderation    │   - Requests     │  - Filters            │
└──────────────────┴──────────────────┴───────────────────────┘
                          ↓ (HTTP/REST)
┌─────────────────────────────────────────────────────────────┐
│              NGINX REVERSE PROXY (80/443)                    │
│  - Load balancing                                            │
│  - CORS handling                                             │
│  - Rate limiting                                             │
│  - SSL termination                                           │
└─────────────────────────────────────────────────────────────┘
              ↙              ↓              ↘
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│ DJANGO (8000)    │  │ LARAVEL      │  │ JAVA (8002)      │
│ - Auth           │  │ (8001)       │  │ - Geolocation    │
│ - ML Models      │  │ - Main API   │  │ - Distance calc  │
│ - Analytics      │  │ - CRUD ops   │  │ - Proximity      │
└──────────────────┘  └──────────────┘  └──────────────────┘
         ↓                   ↓                    ↓
    PostgreSQL,        MongoDB,            MongoDB,
    MongoDB            Redis                Redis
```

## API Endpoint Mapping

### Authentication Flow

**POST /api/auth/login/**
```javascript
// Request
{
  "email": "user@example.com",
  "password": "secure_password"
}

// Response
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

All subsequent requests include:
```
Authorization: Bearer {access_token}
```

### User Management

```
GET    /api/users/me/              - Get current user profile
PATCH  /api/users/me/              - Update profile
GET    /api/users/{id}/            - Get user by ID
```

### Donations (Primary: Laravel)

```
GET    /api/donations/             - List all donations
POST   /api/donations/             - Create donation
GET    /api/donations/{id}/        - Get donation detail
PATCH  /api/donations/{id}/        - Update donation
DELETE /api/donations/{id}/        - Delete donation
POST   /api/donations/{id}/claim/  - Claim a donation
POST   /api/donations/{id}/cancel-claim/  - Cancel claim
```

### Geolocation (Primary: Java)

```
GET    /api/geo/distance/          - Calculate distance between 2 points
GET    /api/geo/nearby/            - Find donations near location
GET    /api/donations/nearby/      - Get nearby donations (alias)
POST   /api/geo/validate/          - Validate location coordinates
```

### Food Requests

```
GET    /api/food-requests/         - List requests
POST   /api/food-requests/         - Create request
GET    /api/food-requests/{id}/    - Get request detail
PATCH  /api/food-requests/{id}/    - Update request
POST   /api/food-requests/{id}/fulfill/  - Fulfill request
```

### Analytics (Primary: Django)

```
GET    /api/analytics/             - Dashboard metrics
GET    /api/analytics/impact-metrics/   - Impact stats
GET    /api/analytics/trends/      - Historical trends
GET    /api/analytics/donors/{id}/ - Donor analytics
```

### ML Models (Django)

```
POST   /api/ml/predict-demand/     - Predict donation demand
POST   /api/ml/recommend/          - Get recommendations
POST   /api/ml/detect-anomalies/   - Detect anomalies
```

## Frontend Integration Layers

### Angular Admin Dashboard

**Services:**
```typescript
// backend.service.ts
- register()
- login()
- logout()
- getCurrentUser()
- getDonations()
- claimDonation()
- getAnalytics()
- getImpactMetrics()
```

**Guards:**
```typescript
// auth.guard.ts
- Protects routes requiring authentication
- Redirects to login if not authenticated
```

**Interceptors:**
```typescript
// auth.interceptor.ts
- Adds JWT token to all requests
- Handles token refresh on 401
- Retry failed requests
```

**Usage:**
```typescript
constructor(private backendService: BackendService) {}

ngOnInit() {
  this.backendService.getDonations().subscribe(
    donations => this.donations = donations,
    error => console.error(error)
  );
}
```

### React Consumer App

**API Service:**
```javascript
// services/api.ts
- Axios-based HTTP client
- Automatic JWT injection
- Token refresh logic
- Error handling
```

**Custom Hook:**
```javascript
// useApi hook
const { data, loading, error, execute } = useApi(
  () => apiService.getDonations(),
  []
);
```

**Usage:**
```jsx
import apiService from '../services/api';

export function DonationsPage() {
  const [donations, setDonations] = useState([]);

  useEffect(() => {
    apiService.getDonations().then(setDonations);
  }, []);

  return <div>{donations.map(d => <DonationCard key={d.id} donation={d} />)}</div>;
}
```

### Vue.js Integration Dashboard

**Pinia Stores:**
```typescript
// useAuthStore
- user
- tokens
- isAuthenticated
- loading
- error
- login()
- logout()
- loadCurrentUser()

// useDonationStore
- donations
- currentDonation
- loading
- error
- fetchDonations()
- fetchNearbyDonations()
- claimDonation()
```

**Usage:**
```vue
<template>
  <div v-if="donationStore.loading">Loading...</div>
  <div v-else>
    <div v-for="donation in donationStore.donations" :key="donation.id">
      {{ donation.food_name }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDonationStore } from '@/stores/api';

const donationStore = useDonationStore();

onMounted(() => {
  donationStore.fetchDonations();
});
</script>
```

## Environment Configuration

### Angular (.env files)
```env
# Development
NG_APP_API_URL=http://localhost:8000/api
NG_APP_ENV=development
NG_APP_LOG_LEVEL=debug

# Production
NG_APP_API_URL=https://api.feeding-hearts.com/api
NG_APP_ENV=production
NG_APP_LOG_LEVEL=error
```

### React (.env files)
```env
# Development
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Feeding Hearts Dev
VITE_ENABLE_DEVTOOLS=true

# Production
VITE_API_URL=https://api.feeding-hearts.com/api
VITE_APP_NAME=Feeding Hearts
VITE_ENABLE_DEVTOOLS=false
```

### Vue (.env files)
```env
# Development
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Feeding Hearts Integration Dev
VITE_ENABLE_DEVTOOLS=true

# Production
VITE_API_URL=https://api.feeding-hearts.com/api
VITE_APP_NAME=Feeding Hearts Integration
VITE_ENABLE_DEVTOOLS=false
```

## Running the Full Stack

### Development Mode
```bash
# Start all services
docker-compose -f docker-compose.full.yml up -d

# Frontend apps available at:
# - Angular:  http://localhost:4200
# - React:    http://localhost:5173
# - Vue:      http://localhost:5174
# - Nginx:    http://localhost

# Backend services:
# - Django:   http://localhost:8000/api
# - Laravel:  http://localhost:8001/api
# - Java:     http://localhost:8002/api
```

### Production Mode
```bash
docker-compose -f docker-compose.yml up -d

# All apps served through Nginx at:
# - Admin:        http://feeding-hearts.local/admin
# - Consumer:     http://feeding-hearts.local/app
# - Integration:  http://feeding-hearts.local/integration
```

## Authentication Flow Diagram

```
┌─────────────────┐
│   User Login    │
│   Frontend      │
└────────┬────────┘
         │
         │ POST /auth/login
         ↓
┌─────────────────┐
│ Django/Laravel  │
│   Validate      │
└────────┬────────┘
         │
         │ Return JWT tokens
         ↓
┌─────────────────┐
│  Store in       │
│  localStorage   │
└────────┬────────┘
         │
         │ Add to Authorization header
         ↓
┌─────────────────┐
│  All API calls  │
│ have JWT token  │
└────────┬────────┘
         │
         │ Token expires
         ↓
┌─────────────────┐
│ Auto-refresh    │
│ with refresh    │
│ token           │
└────────┬────────┘
         │
         │ New access token
         ↓
┌─────────────────┐
│  Continue API   │
│  calls          │
└─────────────────┘
```

## Error Handling

### Common HTTP Status Codes

```
200 OK                    - Success
201 Created               - Resource created
204 No Content            - Success with no content
400 Bad Request           - Validation error
401 Unauthorized          - Invalid/expired token
403 Forbidden             - No permission
404 Not Found             - Resource not found
409 Conflict              - Duplicate/conflict
429 Too Many Requests     - Rate limited
500 Internal Server Error - Server error
503 Service Unavailable   - Service down
```

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {
    "field": ["error message"]
  }
}
```

### Frontend Error Handling

**Angular:**
```typescript
this.backendService.getDonations().subscribe(
  donations => { /* success */ },
  error => {
    if (error.status === 401) {
      // Handle auth error
    } else if (error.status === 429) {
      // Handle rate limit
    } else {
      // Handle other errors
    }
  }
);
```

**React:**
```javascript
try {
  const donations = await apiService.getDonations();
} catch (error) {
  if (error.response?.status === 401) {
    // Handle auth error
  } else {
    // Handle other errors
  }
}
```

**Vue:**
```typescript
try {
  await donationStore.fetchDonations();
} catch (error) {
  // Error is stored in donationStore.error
  console.error(donationStore.error);
}
```

## CORS Configuration

### Nginx Configuration
```nginx
if ($request_method = 'OPTIONS') {
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    add_header 'Access-Control-Max-Age' '86400' always;
    return 204;
}
```

### Backend CORS Headers
All backend services should return:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

## Rate Limiting

```
API Requests:   100 requests/second per IP
App Requests:   50 requests/second per IP
Burst:          100 additional requests allowed
Window:         1 minute
```

## Caching Strategy

```
Static Assets:  30 days (versioned in production)
API Data:       5 minutes (configurable per endpoint)
User Profile:   Session-based
```

## Development Best Practices

1. **Always use environment variables for API URLs**
2. **Store JWT tokens only in localStorage (vulnerable but simpler for web apps)**
3. **Implement token refresh before expiration when possible**
4. **Use proper error boundaries in React**
5. **Use try-catch in async/await operations**
6. **Log API calls in development mode**
7. **Test API integration thoroughly**
8. **Monitor rate limiting and adjust if needed**
9. **Use request timeouts (30s for HTTP, 60s for uploads)**
10. **Implement retry logic for failed requests (exponential backoff)**

## Troubleshooting

### "CORS error" 
- Check Nginx configuration
- Verify backend CORS headers
- Check browser console for specific origin error

### "401 Unauthorized"
- Token may be expired
- Check token refresh implementation
- Clear localStorage and re-login

### "Network timeout"
- Check backend service health
- Increase timeout if processing long operations
- Check Docker container logs

### "API returns 500"
- Check backend service logs
- Verify database connections
- Check environment variables

### Frontend not connecting to backend
- Verify API_URL in .env files
- Check Nginx reverse proxy configuration
- Test direct backend connection (curl)
- Check firewall/network settings
