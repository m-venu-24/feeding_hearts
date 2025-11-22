# Error Logging System - Architecture & Flow Diagrams

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          FEEDING HEARTS PLATFORM                              │
│                                                                                │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┬─────────────┐  │
│  │   Django     │   Laravel    │    Java      │   React     │   Angular   │  │
│  │  AI/ML API   │   Web API    │    GEO API   │   Frontend  │   Admin     │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┴─────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                           ERROR CAPTURE LAYER                             │ │
│  │                                                                            │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────┐  │ │
│  │  │  Middleware    │  │  Decorators    │  │  Client-Side Handlers    │  │ │
│  │  │  (Django)      │  │  (All Frameworks)│ │  (JS/Dart Error Events)  │  │ │
│  │  └────────────────┘  └────────────────┘  └──────────────────────────┘  │ │
│  │                                                                            │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────┐  │ │
│  │  │  Exception     │  │   Webhooks     │  │  Custom Logging          │  │ │
│  │  │  Handlers      │  │  (All Services)│  │  (Application Events)    │  │ │
│  │  └────────────────┘  └────────────────┘  └──────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                       ERROR LOGGING REST API                             │ │
│  │                                                                            │ │
│  │  POST   /errors/                    - Log new error                       │ │
│  │  GET    /errors/                    - List errors (with filters)          │ │
│  │  GET    /errors/{id}/               - Get error details                   │ │
│  │  PATCH  /errors/{id}/               - Update error status                 │ │
│  │  POST   /errors/{id}/resolve/       - Mark resolved                       │ │
│  │  POST   /errors/{id}/assign/        - Assign to developer                 │ │
│  │  POST   /errors/{id}/escalate/      - Escalate error                      │ │
│  │  GET    /errors/stats/              - Statistics                          │ │
│  │  GET    /errors/critical/           - Critical errors only                │ │
│  │                                                                            │ │
│  │  GET    /developers/                - List developers                      │ │
│  │  GET    /developers/workload/       - Developer workload                   │ │
│  │  POST   /developers/{id}/on-call/   - Set on-call status                  │ │
│  │                                                                            │ │
│  │  GET    /patterns/                  - List error patterns                 │ │
│  │  GET    /notifications/             - List notifications                  │ │
│  │                                                                            │ │
│  │  WEBHOOK ENDPOINTS:                                                       │ │
│  │  POST   /webhook/laravel/           - Receive Laravel errors              │ │
│  │  POST   /webhook/java/              - Receive Java errors                 │ │
│  │  POST   /webhook/frontend/          - Receive frontend errors             │ │
│  │  POST   /webhook/mobile/            - Receive mobile errors               │ │
│  │  POST   /webhook/generic/           - Receive generic errors              │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │               ERROR PROCESSING & NOTIFICATION SERVICE                     │ │
│  │                                                                            │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                  Notification Service                                │ │ │
│  │  │                                                                     │ │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │ │ │
│  │  │  │  Email   │  │  Slack   │  │   SMS    │  │ Webhooks│         │ │ │
│  │  │  │ Channel  │  │ Channel  │  │ Channel  │  │ Channel │         │ │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │ │ │
│  │  │                                                                     │ │ │
│  │  │  Features:                                                          │ │ │
│  │  │  - Severity-based routing                                          │ │ │
│  │  │  - On-call schedule awareness                                      │ │ │
│  │  │  - Retry with exponential backoff                                  │ │ │
│  │  │  - Notification audit trail                                        │ │ │
│  │  │  - Developer preferences                                           │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                            │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │              Celery Async Task Processing (Redis Queue)             │ │ │
│  │  │                                                                     │ │ │
│  │  │  - retry_failed_notifications()        [Hourly]                    │ │ │
│  │  │  - analyze_error_patterns()            [Daily]                     │ │ │
│  │  │  - escalate_unresolved_errors()        [Every 6 hours]             │ │ │
│  │  │  - clean_old_error_logs()              [Daily]                     │ │ │
│  │  │  - generate_daily_error_summary()      [Daily 8 AM]                │ │ │
│  │  │  - check_error_thresholds()            [Every 15 min]              │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                          DATA PERSISTENCE LAYER                          │ │
│  │                                                                            │ │
│  │  ┌──────────────────┐              ┌──────────────────┐                  │ │
│  │  │   PostgreSQL     │              │    MongoDB       │                  │ │
│  │  │  (Relational)    │              │   (Document)     │                  │ │
│  │  │                  │              │                  │                  │ │
│  │  │  - error_logs    │              │  - error_logs    │                  │ │
│  │  │  - notifications │              │  - notifications │                  │ │
│  │  │  - patterns      │              │  - patterns      │                  │ │
│  │  │  - assignments   │              │  - assignments   │                  │ │
│  │  │  - stats         │              │                  │                  │ │
│  │  │  - escalations   │              │  JSON Schema     │                  │ │
│  │  │                  │              │  Validation      │                  │ │
│  │  │  20+ Indexes     │              │  12 Indexes      │                  │ │
│  │  │  5 Views         │              │  TTL Auto-cleanup│                  │ │
│  │  │  2 Triggers      │              │  Dual Storage    │                  │ │
│  │  └──────────────────┘              └──────────────────┘                  │ │
│  │                                                                            │ │
│  │  ┌──────────────────┐                                                    │ │
│  │  │     Redis        │                                                    │ │
│  │  │   (Task Queue)   │                                                    │ │
│  │  │                  │                                                    │ │
│  │  │  - Celery Queue  │                                                    │ │
│  │  │  - Task Results  │                                                    │ │
│  │  │  - Caching       │                                                    │ │
│  │  └──────────────────┘                                                    │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                      NOTIFICATION DELIVERY                               │ │
│  │                                                                            │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────┐  │ │
│  │  │  Email Alerts  │  │  Slack Threads │  │  SMS Notifications       │  │ │
│  │  │                │  │                │  │                          │  │ │
│  │  │  - SMTP Server │  │  - Webhooks    │  │  - Twilio API            │  │ │
│  │  │  - HTML Format │  │  - Rich Cards  │  │  - Phone Numbers         │  │ │
│  │  │  - Retry Logic │  │  - Link to Dev │  │  - Critical Only         │  │ │
│  │  └────────────────┘  └────────────────┘  └──────────────────────────┘  │ │
│  │                                                                            │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    Developer Dashboard                             │  │ │
│  │  │                                                                    │  │ │
│  │  │  - Real-time error feed                                           │  │ │
│  │  │  - Error details & stack traces                                   │  │ │
│  │  │  - Assignment & escalation management                             │  │ │
│  │  │  - Statistics & trends                                            │  │ │
│  │  │  - Developer workload view                                        │  │ │
│  │  └────────────────────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Error Flow Diagram

```
┌─────────────────┐
│   Error Occurs  │
│  in Any Service │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Error Capture Mechanism       │
├─────────────────────────────────┤
│ • Exception Handler             │
│ • Middleware                    │
│ • Decorator                     │
│ • Webhook Endpoint              │
│ • Client-side Handler           │
└────────┬────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Error Information Collected     │
├──────────────────────────────────┤
│ • Error Type & Message           │
│ • Stack Trace                    │
│ • User Context                   │
│ • Request/Response Data          │
│ • Severity Classification        │
│ • Service Name                   │
│ • Environment                    │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Error Stored in Database        │
├──────────────────────────────────┤
│ • PostgreSQL (relational)        │
│ • MongoDB (document store)       │
│ • Error ID Generated (UUID)      │
│ • Indexed for fast querying      │
│ • Triggers fire on insert        │
└────────┬─────────────────────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
  ┌────────────────┐            ┌──────────────────┐
  │ Check Severity │            │ Pattern Analysis │
  │                │            │ (Async Task)     │
  │ Critical/High? │            │                  │
  └────┬───────────┘            │ • Group Similar  │
       │                        │ • Count Occur.   │
       │ YES                    │ • Trend Analysis │
       │                        └──────────────────┘
       ▼
  ┌─────────────────────────┐
  │  Immediate Notification │
  │   (Async Task Queue)    │
  └────┬────────────────────┘
       │
       ▼
  ┌──────────────────────────┐
  │  Find Assigned Developer │
  ├──────────────────────────┤
  │ • Match by service       │
  │ • Check if on-call       │
  │ • Load balance           │
  │ • Get preferences        │
  └────┬─────────────────────┘
       │
       ▼
  ┌──────────────────────────┐
  │  Send Notifications      │
  ├──────────────────────────┤
  │ • Email (always)         │
  │ • Slack (high priority)  │
  │ • SMS (critical only)    │
  │ • Custom webhooks        │
  └────┬─────────────────────┘
       │
       ├──── Delivery Tracking
       │     ├─ Success ─────────┐
       │     │                   │
       │     └─ Failure ────┐    │
       │                   │    │
       │                   ▼    ▼
       │               ┌──────────────┐
       │               │ Notification │
       │               │ Log Entry    │
       │               │ Created      │
       │               └──────────────┘
       │
       └─ Retry Queue (if failed)
          After 1 hour
          Max 3 retries

```

## Escalation Flow Diagram

```
┌────────────────────────────────────────────────────────────┐
│           Escalation Rule Engine (Every 6 Hours)           │
└────────┬───────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────┐
         │                                                 │
         ▼                                                 ▼
    ┌─────────────┐                                ┌──────────────┐
    │   Critical  │                                │     High     │
    │  Unresolved │                                │  Unresolved  │
    │  > 1 Hour   │                                │  > 4 Hours   │
    └──────┬──────┘                                └──────┬───────┘
           │                                             │
           ▼                                             ▼
    ┌──────────────────────┐                   ┌──────────────────────┐
    │  Find Manager/Lead   │                   │  Find Manager/Lead   │
    │  for Service         │                   │  for Service         │
    └──────┬───────────────┘                   └──────┬───────────────┘
           │                                         │
           ▼                                         ▼
    ┌──────────────────────┐                   ┌──────────────────────┐
    │ Create Escalation    │                   │ Create Escalation    │
    │ Record               │                   │ Record               │
    │                      │                   │                      │
    │ Level: 1             │                   │ Level: 1             │
    │ Reason: Unresolved   │                   │ Reason: Unresolved   │
    │        > 1h/4h       │                   │        > 4h          │
    └──────┬───────────────┘                   └──────┬───────────────┘
           │                                         │
           ▼                                         ▼
    ┌──────────────────────┐                   ┌──────────────────────┐
    │ Send Notifications   │                   │ Send Notifications   │
    │ to Manager           │                   │ to Manager           │
    │                      │                   │                      │
    │ Email + SMS          │                   │ Email + Slack        │
    └──────────────────────┘                   └──────────────────────┘

```

## Database Schema Relationships

```
┌─────────────────────────────────────────────────────┐
│              PostgreSQL Relations                   │
└─────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │  DeveloperAssignment │
    ├──────────────────────┤
    │ developer_id (PK)    │
    │ name                 │
    │ email                │
    │ services             │
    │ on_call              │
    │ current_load         │
    │ max_load             │
    └──────────────────────┘
              ▲
              │ assigned_to
              │
    ┌─────────────────────────────────┐
    │          ErrorLog               │
    ├─────────────────────────────────┤
    │ error_id (PK)                   │
    │ service                         │
    │ severity                        │
    │ error_type                      │
    │ message                         │
    │ endpoint                        │
    │ stack_trace                     │
    │ resolved                        │
    │ resolved_by                     │
    │ timestamp                       │
    │ assigned_to (FK) ───────────────┤
    └──────────┬──────────────────────┘
               │
    ┌──────────┴────────────────────────────────────┐
    │                                               │
    ▼                                               ▼
┌──────────────────────┐                 ┌──────────────────────┐
│ ErrorNotification    │                 │  ErrorEscalation     │
├──────────────────────┤                 ├──────────────────────┤
│ notification_id      │                 │ escalation_id        │
│ error_id (FK)        │                 │ error_id (FK)        │
│ recipient            │                 │ escalated_from       │
│ channel              │                 │ escalated_to         │
│ status               │                 │ escalation_level     │
│ message_subject      │                 │ reason               │
│ retry_count          │                 │ created_at           │
│ sent_at              │                 └──────────────────────┘
└──────────────────────┘

    ┌────────────────────────────┐
    │    ErrorPattern            │
    ├────────────────────────────┤
    │ pattern_id (PK)            │
    │ service                    │
    │ error_type                 │
    │ occurrence_count           │
    │ affected_services          │
    │ common_endpoints           │
    │ severity_distribution      │
    │ last_occurrence            │
    │ detected_at                │
    └────────────────────────────┘

    ┌────────────────────────────┐
    │    ErrorStats              │
    ├────────────────────────────┤
    │ stat_date (PK)             │
    │ service                    │
    │ total_errors               │
    │ by_severity                │
    │ by_status                  │
    │ avg_resolution_time        │
    │ created_at                 │
    └────────────────────────────┘
```

## Notification Routing Decision Tree

```
┌─────────────────┐
│   Error Logged  │
└────────┬────────┘
         │
         ▼
    ┌─────────────────┐
    │ Get Severity    │
    └────────┬────────┘
             │
    ┌────────┴────────────────┬──────────────────┬──────────────────┐
    │                         │                  │                  │
    ▼                         ▼                  ▼                  ▼
┌─────────────┐      ┌──────────────┐   ┌──────────────┐  ┌──────────────┐
│  Critical   │      │     High     │   │    Medium    │  │  Low/Info    │
└──────┬──────┘      └────────┬─────┘   └──────┬───────┘  └──────┬───────┘
       │                      │                │                 │
       ▼                      ▼                ▼                 ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  Find Developers with Expertise for Service                    │
   └────────┬───────────────────────────────────────────────────────┘
            │
            ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  Filter: Only On-Call Developers                               │
   └────────┬───────────────────────────────────────────────────────┘
            │
            ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  Filter: Current Load < Max Load                               │
   └────────┬───────────────────────────────────────────────────────┘
            │
            ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  Sort: By Current Load (ascending) - Round Robin               │
   └────────┬───────────────────────────────────────────────────────┘
            │
            ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  Select First Developer in List                                │
   └────────┬───────────────────────────────────────────────────────┘
            │
            ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  Determine Notification Channels (by severity)                 │
   │                                                                 │
   │  Critical   ────→  [Email, Slack, SMS]                         │
   │  High      ────→  [Email, Slack]                               │
   │  Medium    ────→  [Email]                                      │
   │  Low/Info  ────→  [Dashboard Only]                             │
   └────────┬───────────────────────────────────────────────────────┘
            │
            ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  Queue Notification Tasks (Async via Redis/Celery)             │
   │                                                                 │
   │  - Immediate dispatch (< 1 second)                             │
   │  - Retry on failure (exponential backoff)                      │
   │  - Track delivery status                                       │
   │  - Log in notification audit trail                             │
   └────────────────────────────────────────────────────────────────┘
```

## Monitoring & Alerting Flow

```
┌─────────────────────────────────────────┐
│  Metrics Collection (Every 15 minutes)  │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────────┐  ┌──────────────┐
│ Error  │  │ Critical   │  │  Escalation  │
│ Count  │  │ Error      │  │  Queue Size  │
└───┬────┘  │ Count      │  └──────┬───────┘
    │       └────┬───────┘         │
    │            │                 │
    └────────────┼─────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  Check Against Thresholds          │
    │                                    │
    │  - > 100 errors/hour?              │
    │  - > 50 critical/hour?             │
    │  - Error rate increasing?          │
    │  - Escalation queue > 10?          │
    └────────────────┬────────────────────┘
                     │
                NO   │   YES
           ┌─────────┴──────────┐
           │                    │
           ▼                    ▼
      ┌────────┐           ┌──────────────────┐
      │ Log to │           │ Send Alert Email │
      │Database│           │ to Admins        │
      └────────┘           │                  │
                          │ Action Items:    │
                          │ - Review Errors  │
                          │ - Add Resources  │
                          │ - Escalate Team  │
                          └──────────────────┘
```

---

## Summary

The error logging system implements a sophisticated, multi-layered architecture that:

1. **Captures** errors from all services automatically
2. **Processes** them asynchronously using Celery task queue
3. **Analyzes** patterns and identifies trends
4. **Detects** thresholds and anomalies
5. **Routes** notifications to appropriate developers
6. **Escalates** critical issues automatically
7. **Tracks** all activities in the database
8. **Provides** comprehensive APIs for querying and management

The system is designed for scalability, reliability, and ease of integration with existing microservices.
