#!/bin/bash

# Docker Health Check Verification Script
# Verifies all services are running and healthy in docker-compose.full.yml

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.full.yml"
DOCKER_NETWORK="feeding-hearts-network"
TIMEOUT=60
CHECK_INTERVAL=5

# Helper functions
print_header() {
  echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

check_service() {
  local service=$1
  local timeout=$2
  local elapsed=0
  
  echo -e "${YELLOW}Checking $service...${NC}"
  
  while [ $elapsed -lt $timeout ]; do
    if docker-compose -f "$COMPOSE_FILE" ps $service 2>/dev/null | grep -q "healthy\|running"; then
      echo -e "${GREEN}✓ $service is healthy${NC}"
      return 0
    fi
    
    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))
  done
  
  echo -e "${RED}✗ $service failed to become healthy within ${timeout}s${NC}"
  return 1
}

check_endpoint() {
  local service=$1
  local host=$2
  local port=$3
  local timeout=$4
  local elapsed=0
  
  echo -e "${YELLOW}Checking $service endpoint ($host:$port)...${NC}"
  
  while [ $elapsed -lt $timeout ]; do
    if docker-compose -f "$COMPOSE_FILE" exec -T $service \
      curl -s --connect-timeout 2 "http://$host:$port/health" >/dev/null 2>&1; then
      echo -e "${GREEN}✓ $service endpoint is responsive${NC}"
      return 0
    fi
    
    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))
  done
  
  echo -e "${RED}✗ $service endpoint not responding after ${timeout}s${NC}"
  return 1
}

test_inter_service_communication() {
  local from_service=$1
  local to_service=$2
  local to_host=$3
  local to_port=$4
  
  echo -e "${YELLOW}Testing communication from $from_service to $to_service...${NC}"
  
  if docker-compose -f "$COMPOSE_FILE" exec -T $from_service \
    curl -s --connect-timeout 5 "http://$to_host:$to_port" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ $from_service can reach $to_service${NC}"
    return 0
  else
    echo -e "${RED}✗ $from_service cannot reach $to_service${NC}"
    return 1
  fi
}

check_database_connection() {
  local service=$1
  local db_type=$2
  local db_host=$3
  local db_port=$4
  
  echo -e "${YELLOW}Testing $db_type database connection from $service...${NC}"
  
  case $db_type in
    mongodb)
      if docker-compose -f "$COMPOSE_FILE" exec -T $service \
        mongosh --host $db_host:$db_port --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $service can connect to MongoDB${NC}"
        return 0
      fi
      ;;
    postgres)
      if docker-compose -f "$COMPOSE_FILE" exec -T $service \
        psql -h $db_host -p $db_port -U postgres -c "SELECT 1" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $service can connect to PostgreSQL${NC}"
        return 0
      fi
      ;;
    redis)
      if docker-compose -f "$COMPOSE_FILE" exec -T $service \
        redis-cli -h $db_host -p $db_port ping >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $service can connect to Redis${NC}"
        return 0
      fi
      ;;
  esac
  
  echo -e "${RED}✗ $service cannot connect to $db_type${NC}"
  return 1
}

check_api_endpoint() {
  local service=$1
  local endpoint=$2
  local expected_status=$3
  
  echo -e "${YELLOW}Testing API endpoint: $endpoint${NC}"
  
  status=$(docker-compose -f "$COMPOSE_FILE" exec -T $service \
    curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")
  
  if [ "$status" = "$expected_status" ]; then
    echo -e "${GREEN}✓ Endpoint returned expected status $status${NC}"
    return 0
  else
    echo -e "${RED}✗ Endpoint returned $status (expected $expected_status)${NC}"
    return 1
  fi
}

# Verify compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
  echo -e "${RED}Error: $COMPOSE_FILE not found${NC}"
  exit 1
fi

# Main execution
print_header "1. Docker Compose Environment Check"

echo "Compose file: $COMPOSE_FILE"
echo "Network: $DOCKER_NETWORK"
echo ""

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d
sleep 10

print_header "2. Service Health Check"

FAILED=0

# Check all services
SERVICES=("mongodb" "postgres" "redis" "django" "laravel" "java-service" "nginx")

for service in "${SERVICES[@]}"; do
  if ! check_service "$service" "$TIMEOUT"; then
    FAILED=$((FAILED + 1))
  fi
  echo ""
done

print_header "3. Inter-Service Communication Check"

# Test service connectivity
test_inter_service_communication "django" "mongodb" "mongodb" "27017" || FAILED=$((FAILED + 1))
echo ""

test_inter_service_communication "laravel" "postgres" "postgres" "5432" || FAILED=$((FAILED + 1))
echo ""

test_inter_service_communication "java-service" "redis" "redis" "6379" || FAILED=$((FAILED + 1))
echo ""

test_inter_service_communication "nginx" "django" "django" "8000" || FAILED=$((FAILED + 1))
echo ""

test_inter_service_communication "nginx" "laravel" "laravel" "8001" || FAILED=$((FAILED + 1))
echo ""

print_header "4. Database Connection Check"

check_database_connection "django" "mongodb" "mongodb" "27017" || FAILED=$((FAILED + 1))
echo ""

check_database_connection "laravel" "postgres" "postgres" "5432" || FAILED=$((FAILED + 1))
echo ""

check_database_connection "java-service" "redis" "redis" "6379" || FAILED=$((FAILED + 1))
echo ""

print_header "5. API Endpoint Check"

# Give services time to start
sleep 5

check_api_endpoint "nginx" "http://localhost/api/auth/login/" "405" || FAILED=$((FAILED + 1))
echo ""

check_api_endpoint "django" "http://localhost:8000/api/donations/" "401" || FAILED=$((FAILED + 1))
echo ""

print_header "6. Service Logs Check"

echo -e "${YELLOW}Recent logs from all services:${NC}"
echo ""

for service in "${SERVICES[@]}"; do
  echo -e "${BLUE}--- $service logs (last 5 lines) ---${NC}"
  docker-compose -f "$COMPOSE_FILE" logs --tail 5 "$service" 2>/dev/null | tail -3 || echo "No logs available"
  echo ""
done

print_header "7. Docker Network Check"

echo -e "${YELLOW}Connected networks:${NC}"
docker network inspect $DOCKER_NETWORK 2>/dev/null | \
  grep -A 20 '"Containers"' | grep -E '"Name"|"IPv4Address"' || echo "Network not found"
echo ""

print_header "8. Resource Usage Check"

echo -e "${YELLOW}Container resource usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "Stats unavailable"
echo ""

print_header "9. Volume Check"

echo -e "${YELLOW}Mounted volumes:${NC}"
for service in "${SERVICES[@]}"; do
  docker-compose -f "$COMPOSE_FILE" exec -T "$service" df -h 2>/dev/null | grep -E "Filesystem|feeding" || true
done
echo ""

print_header "10. Summary"

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ All checks passed!${NC}"
  echo ""
  echo -e "${GREEN}Services Status:${NC}"
  docker-compose -f "$COMPOSE_FILE" ps
  exit 0
else
  echo -e "${RED}✗ $FAILED check(s) failed${NC}"
  echo ""
  echo -e "${RED}Failed Services:${NC}"
  docker-compose -f "$COMPOSE_FILE" ps --filter "status=exited"
  echo ""
  echo -e "${YELLOW}Troubleshooting:${NC}"
  echo "1. Check logs: docker-compose logs <service-name>"
  echo "2. Restart service: docker-compose restart <service-name>"
  echo "3. View resource usage: docker stats"
  echo "4. Check network: docker network inspect $DOCKER_NETWORK"
  exit 1
fi
