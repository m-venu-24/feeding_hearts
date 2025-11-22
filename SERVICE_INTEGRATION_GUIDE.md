# Service-Specific Error Logging Integration Guide

## Django Backend Integration

### 1. Enable Middleware

**File:** `backend/django-ai-ml/settings.py`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Add error logging middleware
    'error_logging.middleware.ErrorLoggingMiddleware',
]

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_log_handler': {
            '()': 'error_logging.middleware.DjangoLoggerHandler',
            'level': 'WARNING',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['error_log_handler', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Use in Views

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from error_logging.middleware import error_capture_decorator
from error_logging.models import ErrorLog

class DonationView(APIView):
    @error_capture_decorator
    def post(self, request):
        try:
            amount = request.data.get('amount')
            if amount <= 0:
                raise ValueError('Invalid amount')
            # Process donation
            return Response({'status': 'success'})
        except Exception as e:
            # Error is automatically logged by middleware
            raise

# Or manually log
def manual_logging_example(request):
    try:
        # Some operation
        pass
    except Exception as e:
        ErrorLog.objects.create(
            service='django',
            severity='high',
            error_type=type(e).__name__,
            message=str(e),
            endpoint=request.path,
            user_id=request.user.id if request.user.is_authenticated else None,
        )
        raise
```

---

## Laravel Backend Integration

### 1. Create Error Handler Service

**File:** `backend/laravel-web/app/Services/ErrorLoggingService.php`

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ErrorLoggingService
{
    private $errorLoggingUrl;

    public function __construct()
    {
        $this->errorLoggingUrl = env('ERROR_LOGGING_URL', 'http://django:8000/api/error-logging/webhook/laravel/');
    }

    /**
     * Log error to central error logging system
     */
    public function logError(
        string $errorType,
        string $message,
        string $severity = 'medium',
        string $endpoint = null,
        int $code = null,
        string $stackTrace = null,
        array $context = []
    ): bool {
        try {
            $errorData = [
                'error_type' => $errorType,
                'message' => $message,
                'severity' => $severity,
                'endpoint' => $endpoint ?? request()->path(),
                'code' => $code ?? 500,
                'stack_trace' => $stackTrace,
                'context' => array_merge([
                    'user_id' => auth()->id(),
                    'ip_address' => request()->ip(),
                    'user_agent' => request()->userAgent(),
                ], $context),
                'environment' => env('APP_ENV', 'production'),
            ];

            $response = Http::timeout(5)->post($this->errorLoggingUrl, $errorData);

            if ($response->successful()) {
                Log::info('Error logged to central system', [
                    'error_id' => $response->json('error_id')
                ]);
                return true;
            } else {
                Log::error('Failed to log error to central system', [
                    'status' => $response->status(),
                ]);
                return false;
            }
        } catch (\Exception $e) {
            Log::error('Error logging service failed', [
                'error' => $e->getMessage(),
            ]);
            return false;
        }
    }
}
```

### 2. Register in Service Provider

**File:** `backend/laravel-web/app/Providers/AppServiceProvider.php`

```php
<?php

namespace App\Providers;

use App\Services\ErrorLoggingService;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register()
    {
        $this->app->singleton(ErrorLoggingService::class, function ($app) {
            return new ErrorLoggingService();
        });
    }
}
```

### 3. Use in Exception Handler

**File:** `backend/laravel-web/app/Exceptions/Handler.php`

```php
<?php

namespace App\Exceptions;

use App\Services\ErrorLoggingService;
use Illuminate\Foundation\Exceptions\Handler as ExceptionHandler;
use Throwable;

class Handler extends ExceptionHandler
{
    public function render($request, Throwable $exception)
    {
        // Log to central error system
        $errorLoggingService = app(ErrorLoggingService::class);
        
        $severity = $this->getSeverity($exception);
        
        $errorLoggingService->logError(
            get_class($exception),
            $exception->getMessage(),
            $severity,
            $request->path(),
            $this->getStatusCode($exception),
            $exception->getTraceAsString(),
            [
                'method' => $request->method(),
                'input' => $request->except(['password', 'password_confirmation']),
            ]
        );

        return parent::render($request, $exception);
    }

    private function getSeverity(Throwable $exception): string
    {
        if ($exception instanceof \Illuminate\Database\Eloquent\ModelNotFoundException) {
            return 'low';
        } elseif ($exception instanceof \Illuminate\Validation\ValidationException) {
            return 'medium';
        } elseif ($exception instanceof \Illuminate\Database\QueryException) {
            return 'high';
        }
        return 'high';
    }

    private function getStatusCode(Throwable $exception): int
    {
        return method_exists($exception, 'getStatusCode') 
            ? $exception->getStatusCode() 
            : 500;
    }
}
```

### 4. Usage in Controllers

```php
<?php

namespace App\Http\Controllers;

use App\Services\ErrorLoggingService;

class DonationController extends Controller
{
    public function __construct(private ErrorLoggingService $errorLoggingService)
    {}

    public function store(Request $request)
    {
        try {
            $validated = $request->validate([
                'amount' => 'required|numeric|min:1',
                'recipient_id' => 'required|exists:recipients,id',
            ]);

            // Process donation
            $donation = Donation::create($validated);
            
            return response()->json($donation, 201);
        } catch (\Exception $e) {
            $this->errorLoggingService->logError(
                get_class($e),
                $e->getMessage(),
                'high',
                $request->path(),
                500,
                $e->getTraceAsString()
            );
            throw $e;
        }
    }
}
```

---

## Java Spring Boot Integration

### 1. Create Error Logger Service

**File:** `backend/java-geolocation/src/main/java/com/feedinghearts/service/ErrorLoggingService.java`

```java
package com.feedinghearts.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import lombok.extern.slf4j.Slf4j;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class ErrorLoggingService {
    
    private final WebClient webClient;
    private final String errorLoggingUrl;
    
    public ErrorLoggingService(
        WebClient.Builder webClientBuilder,
        @Value("${error-logging.url:http://django:8000/api/error-logging/webhook/java/}") String errorLoggingUrl
    ) {
        this.webClient = webClientBuilder.build();
        this.errorLoggingUrl = errorLoggingUrl;
    }
    
    /**
     * Log error to central error logging system
     */
    public void logError(
        String errorType,
        String message,
        String severity,
        String endpoint,
        Integer code,
        String stackTrace,
        Map<String, Object> context
    ) {
        try {
            Map<String, Object> errorData = new HashMap<>();
            errorData.put("errorType", errorType);
            errorData.put("message", message);
            errorData.put("severity", severity);
            errorData.put("endpoint", endpoint);
            errorData.put("code", code);
            errorData.put("stackTrace", stackTrace);
            errorData.put("context", context != null ? context : new HashMap<>());
            errorData.put("environment", System.getenv().getOrDefault("ENVIRONMENT", "production"));
            
            webClient.post()
                .uri(errorLoggingUrl)
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(errorData)
                .retrieve()
                .bodyToMono(Map.class)
                .doOnSuccess(response -> {
                    log.info("Error logged to central system: {}", response.get("error_id"));
                })
                .doOnError(error -> {
                    log.error("Failed to log error to central system", error);
                })
                .subscribe();
        } catch (Exception e) {
            log.error("Error logging service failed", e);
        }
    }
    
    /**
     * Log exception
     */
    public void logException(String endpoint, Exception exception) {
        Map<String, Object> context = new HashMap<>();
        context.put("timestamp", LocalDateTime.now());
        context.put("exceptionClass", exception.getClass().getName());
        
        logError(
            exception.getClass().getSimpleName(),
            exception.getMessage(),
            "high",
            endpoint,
            500,
            getStackTrace(exception),
            context
        );
    }
    
    private String getStackTrace(Exception exception) {
        StringBuilder sb = new StringBuilder();
        for (StackTraceElement element : exception.getStackTrace()) {
            sb.append(element.toString()).append("\n");
        }
        return sb.toString();
    }
}
```

### 2. Create Exception Handler

**File:** `backend/java-geolocation/src/main/java/com/feedinghearts/exception/GlobalExceptionHandler.java`

```java
package com.feedinghearts.exception;

import com.feedinghearts.service.ErrorLoggingService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestControllerAdvice
@RequiredArgsConstructor
public class GlobalExceptionHandler {
    
    private final ErrorLoggingService errorLoggingService;
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGlobalException(
        Exception ex,
        WebRequest request
    ) {
        // Log to central error system
        errorLoggingService.logException(request.getDescription(false), ex);
        
        Map<String, Object> response = new HashMap<>();
        response.put("error", ex.getMessage());
        response.put("path", request.getDescription(false));
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(500).body(response);
    }
    
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalArgument(
        IllegalArgumentException ex,
        WebRequest request
    ) {
        Map<String, Object> context = new HashMap<>();
        context.put("errorType", "IllegalArgumentException");
        
        errorLoggingService.logError(
            "IllegalArgumentException",
            ex.getMessage(),
            "medium",
            request.getDescription(false),
            400,
            getStackTrace(ex),
            context
        );
        
        Map<String, Object> response = new HashMap<>();
        response.put("error", ex.getMessage());
        return ResponseEntity.badRequest().body(response);
    }
    
    private String getStackTrace(Exception exception) {
        StringBuilder sb = new StringBuilder();
        for (StackTraceElement element : exception.getStackTrace()) {
            sb.append(element.toString()).append("\n");
        }
        return sb.toString();
    }
}
```

### 3. Use in Services

```java
@Service
@RequiredArgsConstructor
public class GeolocationService {
    
    private final ErrorLoggingService errorLoggingService;
    
    public LocationResponse findNearestDonationCenters(double latitude, double longitude) {
        try {
            // Service logic
            return calculateNearestCenters(latitude, longitude);
        } catch (InvalidCoordinatesException e) {
            errorLoggingService.logException("/api/geolocation/nearby", e);
            throw e;
        }
    }
}
```

---

## Frontend Integration (React)

### 1. Create Error Logger Hook

**File:** `frontend/react-app/src/hooks/useErrorLogging.ts`

```typescript
import { useCallback } from 'react';

interface ErrorContext {
  userId?: string;
  endpoint?: string;
  userAgent?: string;
  timestamp?: string;
  [key: string]: any;
}

export const useErrorLogging = () => {
  const logError = useCallback(async (
    errorType: string,
    message: string,
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info' = 'medium',
    context: ErrorContext = {}
  ) => {
    try {
      const errorData = {
        service: 'react',
        errorType,
        message,
        severity,
        endpoint: window.location.pathname,
        userAgent: navigator.userAgent,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        user_id: localStorage.getItem('user_id'),
        ...context,
        environment: process.env.REACT_APP_ENV || 'production',
      };

      await fetch('/api/error-logging/webhook/frontend/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorData),
      });
    } catch (err) {
      console.error('Failed to log error:', err);
    }
  }, []);

  return { logError };
};
```

### 2. Create Global Error Handler

**File:** `frontend/react-app/src/utils/errorHandler.ts`

```typescript
import { useErrorLogging } from '../hooks/useErrorLogging';

// Setup global error handler
export const setupGlobalErrorHandler = () => {
  const { logError } = useErrorLogging();

  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    logError(
      event.error?.name || 'Error',
      event.message,
      'high',
      {
        source: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      }
    );
  });

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    logError(
      'UnhandledPromiseRejection',
      event.reason?.message || String(event.reason),
      'high'
    );
  });
};
```

### 3. Use in Components

```typescript
import { useErrorLogging } from './hooks/useErrorLogging';

export const DonationForm = () => {
  const { logError } = useErrorLogging();

  const handleSubmit = async (data) => {
    try {
      const response = await fetch('/api/donations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      await logError(
        'DonationSubmitError',
        error.message,
        'high',
        { formData: data }
      );
      // Show user-friendly message
      setError('Failed to submit donation');
    }
  };

  return (
    // Component JSX
  );
};
```

---

## Frontend Integration (Angular)

### 1. Create Error Logging Service

**File:** `frontend/angular-admin/src/app/services/error-logging.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface ErrorData {
  service: string;
  errorType: string;
  message: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  endpoint: string;
  [key: string]: any;
}

@Injectable({
  providedIn: 'root'
})
export class ErrorLoggingService {
  private webhookUrl = '/api/error-logging/webhook/frontend/';

  constructor(private http: HttpClient) {}

  logError(
    errorType: string,
    message: string,
    severity: string = 'medium',
    context: any = {}
  ) {
    const errorData: ErrorData = {
      service: 'angular',
      errorType,
      message,
      severity,
      endpoint: window.location.pathname,
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      user_id: localStorage.getItem('user_id'),
      ...context,
      environment: 'production',
    };

    this.http.post(this.webhookUrl, errorData).subscribe({
      next: (response: any) => {
        console.log('Error logged:', response.error_id);
      },
      error: (err) => {
        console.error('Failed to log error:', err);
      },
    });
  }
}
```

### 2. Create Error Handler

**File:** `frontend/angular-admin/src/app/core/error.handler.ts`

```typescript
import { ErrorHandler, Injectable, Injector } from '@angular/core';
import { ErrorLoggingService } from '../services/error-logging.service';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  constructor(private injector: Injector) {}

  handleError(error: Error) {
    const errorLoggingService = this.injector.get(ErrorLoggingService);

    errorLoggingService.logError(
      error.name,
      error.message,
      'high',
      {
        stack: error.stack,
      }
    );

    console.error('An error occurred:', error);
  }
}
```

### 3. Register in App Module

```typescript
import { ErrorHandler } from '@angular/core';
import { GlobalErrorHandler } from './core/error.handler';

@NgModule({
  providers: [
    { provide: ErrorHandler, useClass: GlobalErrorHandler },
  ],
})
export class AppModule {}
```

---

## Frontend Integration (Vue)

### 1. Create Error Logging Plugin

**File:** `frontend/vue-integration/src/plugins/errorLogging.ts`

```typescript
import { App } from 'vue';

interface ErrorOptions {
  errorType: string;
  message: string;
  severity?: 'critical' | 'high' | 'medium' | 'low' | 'info';
  context?: Record<string, any>;
}

export default {
  install(app: App) {
    app.config.errorHandler = (err: any, instance, info) => {
      const errorLogging = app.config.globalProperties.$errorLogging;
      errorLogging?.logError(
        (err as Error).name,
        (err as Error).message,
        'high',
        { info }
      );
    };

    app.config.globalProperties.$errorLogging = {
      async logError(
        errorType: string,
        message: string,
        severity: string = 'medium',
        context: Record<string, any> = {}
      ) {
        try {
          const errorData = {
            service: 'vue',
            errorType,
            message,
            severity,
            endpoint: window.location.pathname,
            userAgent: navigator.userAgent,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            user_id: localStorage.getItem('user_id'),
            ...context,
            environment: 'production',
          };

          await fetch('/api/error-logging/webhook/frontend/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(errorData),
          });
        } catch (err) {
          console.error('Failed to log error:', err);
        }
      },
    };
  },
};
```

### 2. Register in Main

```typescript
import { createApp } from 'vue';
import App from './App.vue';
import errorLogging from './plugins/errorLogging';

const app = createApp(App);
app.use(errorLogging);
app.mount('#app');
```

### 3. Use in Components

```vue
<script setup>
import { useErrorLogging } from './composables/useErrorLogging';

const { logError } = useErrorLogging();

const submitForm = async (formData) => {
  try {
    const response = await fetch('/api/donations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    await logError(
      'FormSubmitError',
      error.message,
      'high',
      { formData }
    );
  }
};
</script>
```

---

## Flutter Mobile Integration

### 1. Create Error Logging Service

**File:** `mobile/flutter/lib/services/error_logging_service.dart`

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:device_info_plus/device_info_plus.dart';

class ErrorLoggingService {
  static const String webhookUrl = 'https://api.feedinghearts.com/api/error-logging/webhook/mobile/';
  
  final DeviceInfoPlugin deviceInfoPlugin = DeviceInfoPlugin();
  
  Future<void> logError({
    required String errorType,
    required String message,
    String severity = 'high',
    String? screenName,
    Map<String, dynamic>? context,
  }) async {
    try {
      final deviceInfo = await _getDeviceInfo();
      
      final errorData = {
        'error_type': errorType,
        'message': message,
        'severity': severity,
        'screen': screenName,
        'device': deviceInfo['device'],
        'os': deviceInfo['os'],
        'app_version': deviceInfo['appVersion'],
        'user_id': _getUserId(),
        'session_id': _getSessionId(),
        'context': context ?? {},
        'environment': 'production',
      };

      final response = await http.post(
        Uri.parse(webhookUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(errorData),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode != 201) {
        print('Failed to log error: ${response.statusCode}');
      }
    } catch (e) {
      print('Error logging failed: $e');
    }
  }

  Future<Map<String, dynamic>> _getDeviceInfo() async {
    try {
      IosDeviceInfo? iosInfo;
      AndroidDeviceInfo? androidInfo;
      
      try {
        iosInfo = await deviceInfoPlugin.iosInfo;
      } catch (e) {
        androidInfo = await deviceInfoPlugin.androidInfo;
      }

      if (iosInfo != null) {
        return {
          'device': iosInfo.model,
          'os': 'iOS ${iosInfo.systemVersion}',
          'appVersion': '1.0.0', // Replace with actual version
        };
      } else if (androidInfo != null) {
        return {
          'device': androidInfo.model,
          'os': 'Android ${androidInfo.version.release}',
          'appVersion': '1.0.0', // Replace with actual version
        };
      }
    } catch (e) {
      print('Failed to get device info: $e');
    }

    return {
      'device': 'Unknown',
      'os': 'Unknown',
      'appVersion': 'Unknown',
    };
  }

  String _getUserId() {
    // Return logged-in user ID
    return 'user-id-here';
  }

  String _getSessionId() {
    // Return current session ID
    return 'session-id-here';
  }
}
```

### 2. Use in Error Handler

```dart
import 'package:flutter/material.dart';
import 'services/error_logging_service.dart';

final errorLoggingService = ErrorLoggingService();

void main() {
  FlutterError.onError = (FlutterErrorDetails details) {
    errorLoggingService.logError(
      errorType: 'FlutterError',
      message: details.exceptionAsString(),
      severity: 'high',
    );
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    errorLoggingService.logError(
      errorType: 'PlatformError',
      message: error.toString(),
      severity: 'critical',
      context: {'stack': stack.toString()},
    );
    return true;
  };

  runApp(const MyApp());
}
```

### 3. Use in Screens

```dart
class DonationScreen extends StatefulWidget {
  @override
  State<DonationScreen> createState() => _DonationScreenState();
}

class _DonationScreenState extends State<DonationScreen> {
  final errorLoggingService = ErrorLoggingService();

  Future<void> submitDonation(DonationData donation) async {
    try {
      final response = await http.post(
        Uri.parse('https://api.feedinghearts.com/api/donations/'),
        body: jsonEncode(donation),
      );

      if (response.statusCode != 201) {
        throw Exception('Failed to submit donation');
      }
    } catch (e) {
      await errorLoggingService.logError(
        errorType: 'DonationSubmitError',
        message: e.toString(),
        severity: 'high',
        screenName: 'DonationScreen',
        context: {'donation': donation.toJson()},
      );
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to submit donation')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Screen UI
    );
  }
}
```

---

## Summary

Each service now has complete error logging integration:
- ✅ Django: Middleware + Decorator
- ✅ Laravel: Service + Exception Handler
- ✅ Java: Service + Global Exception Handler
- ✅ React: Hook + Global Error Handler
- ✅ Angular: Service + Global Error Handler
- ✅ Vue: Plugin + Composable
- ✅ Flutter: Service + Error Handlers

All errors flow to the central error logging database where they are analyzed, patterns detected, and developers notified automatically.
