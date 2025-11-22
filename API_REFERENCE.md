# Feeding Hearts - Complete API Reference

## Base URL
```
Development: http://localhost:8000/api
Production:  https://api.feeding-hearts.com/api
```

## Authentication

### Register User
```http
POST /auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password_123",
  "name": "John Doe"
}

Response: 201
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Login User
```http
POST /auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password_123"
}

Response: 200
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refresh Token
```http
POST /auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response: 200
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## User Management

### Get Current User Profile
```http
GET /users/me/
Authorization: Bearer {access_token}

Response: 200
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar": "https://...",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "New York, NY"
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-02T00:00:00Z"
}
```

### Update Profile
```http
PATCH /users/me/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "John Smith",
  "avatar": "https://new-avatar-url.com",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "New York, NY"
  }
}

Response: 200
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Smith",
  ...
}
```

### Get User by ID
```http
GET /users/{user_id}/
Authorization: Bearer {access_token}

Response: 200
{
  "id": "uuid",
  "name": "John Doe",
  "avatar": "https://...",
  "location": { ... },
  "created_at": "2025-01-01T00:00:00Z"
}
```

## Donations

### List All Donations
```http
GET /donations/?status=available&category=vegetables&limit=10&offset=0
Authorization: Bearer {access_token}

Response: 200
{
  "count": 45,
  "next": "http://localhost:8000/api/donations/?offset=10",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "food_name": "Fresh Tomatoes",
      "categories": ["vegetables", "produce"],
      "quantity": 10,
      "unit": "kg",
      "status": "available",
      "donor_id": "uuid",
      "donor_name": "John's Farm",
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "123 Main St, New York, NY"
      },
      "created_at": "2025-01-02T10:00:00Z",
      "expires_at": "2025-01-03T10:00:00Z",
      "dietary_restrictions": [],
      "verified": true
    },
    ...
  ]
}
```

### Create Donation
```http
POST /donations/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "food_name": "Fresh Tomatoes",
  "categories": ["vegetables", "produce"],
  "quantity": 10,
  "unit": "kg",
  "description": "Ripe organic tomatoes from our garden",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "123 Main St, New York, NY"
  },
  "expiration_hours": 24,
  "dietary_restrictions": ["organic"],
  "image_urls": ["https://..."]
}

Response: 201
{
  "id": "uuid",
  "food_name": "Fresh Tomatoes",
  "status": "available",
  "created_at": "2025-01-02T10:00:00Z",
  "expires_at": "2025-01-03T10:00:00Z",
  ...
}
```

### Get Donation by ID
```http
GET /donations/{donation_id}/
Authorization: Bearer {access_token}

Response: 200
{
  "id": "uuid",
  "food_name": "Fresh Tomatoes",
  "categories": ["vegetables", "produce"],
  "quantity": 10,
  "unit": "kg",
  "status": "available",
  "donor_id": "uuid",
  "location": { ... },
  "created_at": "2025-01-02T10:00:00Z",
  "expires_at": "2025-01-03T10:00:00Z",
  ...
}
```

### Update Donation
```http
PATCH /donations/{donation_id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "quantity": 15,
  "expiration_hours": 12
}

Response: 200
{ ... }
```

### Delete Donation
```http
DELETE /donations/{donation_id}/
Authorization: Bearer {access_token}

Response: 204
```

### Claim Donation
```http
POST /donations/{donation_id}/claim/
Authorization: Bearer {access_token}
Content-Type: application/json

{}

Response: 200
{
  "id": "uuid",
  "status": "claimed",
  "claimed_by": "uuid",
  "claimed_at": "2025-01-02T11:00:00Z",
  ...
}
```

### Cancel Claim
```http
POST /donations/{donation_id}/cancel-claim/
Authorization: Bearer {access_token}

Response: 200
{
  "id": "uuid",
  "status": "available",
  "claimed_by": null,
  "claimed_at": null,
  ...
}
```

## Geolocation & Nearby Search

### Find Nearby Donations
```http
GET /donations/nearby/?latitude=40.7128&longitude=-74.0060&radius=5
Authorization: Bearer {access_token}

Response: 200
{
  "count": 12,
  "results": [
    {
      "id": "uuid",
      "food_name": "Fresh Tomatoes",
      "distance_km": 0.5,
      "location": { ... },
      ...
    },
    ...
  ]
}
```

### Calculate Distance
```http
POST /geo/distance/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "lat1": 40.7128,
  "lon1": -74.0060,
  "lat2": 40.7129,
  "lon2": -74.0061
}

Response: 200
{
  "distance_km": 0.15,
  "distance_miles": 0.09,
  "duration_minutes": 2
}
```

### Get Ranked Nearby Donations
```http
GET /geo/nearby-ranked/?latitude=40.7128&longitude=-74.0060&limit=20
Authorization: Bearer {access_token}

Response: 200
{
  "results": [
    {
      "id": "uuid",
      "food_name": "Fresh Tomatoes",
      "distance_km": 0.5,
      "ranking_score": 0.95,
      "rank": 1,
      ...
    },
    ...
  ]
}
```

## Food Requests

### List Food Requests
```http
GET /food-requests/?status=open&category=vegetables&limit=10
Authorization: Bearer {access_token}

Response: 200
{
  "count": 25,
  "results": [
    {
      "id": "uuid",
      "requester_id": "uuid",
      "categories": ["vegetables"],
      "quantity": 5,
      "urgency": "high",
      "location": { ... },
      "status": "open",
      "created_at": "2025-01-02T10:00:00Z"
    },
    ...
  ]
}
```

### Create Food Request
```http
POST /food-requests/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "categories": ["vegetables", "fruits"],
  "quantity": 10,
  "urgency": "high",
  "dietary_requirements": ["no nuts"],
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "Community Center, New York, NY"
  }
}

Response: 201
{
  "id": "uuid",
  "requester_id": "uuid",
  "status": "open",
  "created_at": "2025-01-02T10:00:00Z",
  ...
}
```

### Fulfill Food Request
```http
POST /food-requests/{request_id}/fulfill/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "donation_id": "uuid"
}

Response: 200
{
  "id": "uuid",
  "status": "fulfilled",
  "fulfilled_by": "uuid",
  "fulfilled_at": "2025-01-02T11:00:00Z",
  ...
}
```

## Analytics

### Get Dashboard Analytics
```http
GET /analytics/
Authorization: Bearer {access_token}

Response: 200
{
  "total_donations": 1250,
  "active_donations": 45,
  "claimed_donations": 890,
  "expired_donations": 315,
  "total_users": 2350,
  "active_donors": 1200,
  "active_requesters": 1150,
  "avg_donation_time_hours": 12.5
}
```

### Get Impact Metrics
```http
GET /analytics/impact-metrics/
Authorization: Bearer {access_token}

Response: 200
{
  "total_food_donated_kg": 50000,
  "people_helped": 5250,
  "meals_distributed": 12500,
  "carbon_saved_kg": 5000,
  "waste_reduced_percent": 25,
  "value_donated": {
    "amount": 250000,
    "currency": "USD"
  }
}
```

### Get User Analytics
```http
GET /analytics/users/{user_id}/
Authorization: Bearer {access_token}

Response: 200
{
  "total_donations": 25,
  "total_claimed": 18,
  "total_requests_created": 5,
  "total_requests_fulfilled": 3,
  "reputation_score": 95,
  "joined_date": "2025-01-01T00:00:00Z",
  "last_activity": "2025-01-02T10:00:00Z"
}
```

## ML Endpoints

### Predict Donation Demand
```http
POST /ml/predict-demand/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "time_range_days": 7,
  "categories": ["vegetables", "fruits"]
}

Response: 200
{
  "predicted_demand": {
    "vegetables": 150,
    "fruits": 80,
    "dairy": 45
  },
  "confidence": 0.87,
  "top_items": [
    {
      "item": "tomatoes",
      "predicted_qty": 45,
      "confidence": 0.92
    }
  ]
}
```

### Get Recommendations
```http
POST /ml/recommend/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user_id": "uuid",
  "limit": 10
}

Response: 200
{
  "recommendations": [
    {
      "id": "uuid",
      "food_name": "Fresh Tomatoes",
      "score": 0.95,
      "reason": "Similar to previously claimed items"
    },
    ...
  ]
}
```

### Detect Anomalies
```http
POST /ml/detect-anomalies/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "donation_id": "uuid"
}

Response: 200
{
  "is_anomaly": false,
  "anomaly_score": 0.15,
  "flags": [],
  "confidence": 0.92
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": {
    "email": ["Enter a valid email address."],
    "password": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "permission_denied",
  "message": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "The requested resource was not found."
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Request rate limit exceeded. Retry after 60 seconds."
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred. Please try again later."
}
```

## Rate Limiting Headers

All responses include:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

## Pagination

Paginated endpoints support:
```http
GET /donations/?limit=20&offset=40

Response includes:
{
  "count": 100,
  "next": "http://localhost:8000/api/donations/?limit=20&offset=60",
  "previous": "http://localhost:8000/api/donations/?limit=20&offset=20",
  "results": [...]
}
```

## Filtering

Supported filter parameters:
```
- status: available, claimed, expired
- category: vegetables, fruits, dairy, proteins, grains
- urgency: low, medium, high
- verified: true, false
- created_after: ISO date string
- created_before: ISO date string
- updated_after: ISO date string
- updated_before: ISO date string
```

## Sorting

```http
GET /donations/?ordering=-created_at

Supported fields:
- created_at
- updated_at
- expires_at
- distance (for geolocation)
- ranking_score (for ML)
```

## Webhooks (Coming Soon)

```
- donation.created
- donation.claimed
- donation.expired
- request.created
- request.fulfilled
- user.created
- user.updated
```
