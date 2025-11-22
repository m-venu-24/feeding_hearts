#!/bin/bash

# E2E Integration Test - Full Workflow Testing
# Tests complete user journeys across all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost/api}"
TEST_USER_EMAIL="e2e-test-$(date +%s)@example.com"
TEST_USER_PASSWORD="TestPassword123!"
TEST_USER_NAME="E2E Test User"

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
  echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║ $1${NC}"
  echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
  echo ""
}

test_case() {
  echo -e "${YELLOW}[TEST] $1${NC}"
  TESTS_RUN=$((TESTS_RUN + 1))
}

assert_status() {
  local response=$1
  local expected=$2
  local message=$3
  
  local status=$(echo "$response" | tail -1)
  
  if [ "$status" = "$expected" ]; then
    echo -e "${GREEN}  ✓ Status $status (expected $expected) - $message${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}  ✗ Status $status (expected $expected) - $message${NC}"
    echo "Response: $response"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

assert_contains() {
  local response=$1
  local text=$2
  local message=$3
  
  if echo "$response" | grep -q "$text"; then
    echo -e "${GREEN}  ✓ Response contains '$text' - $message${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}  ✗ Response does not contain '$text' - $message${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

assert_json() {
  local response=$1
  local field=$2
  local expected=$3
  local message=$4
  
  local value=$(echo "$response" | jq -r ".${field}" 2>/dev/null || echo "null")
  
  if [ "$value" = "$expected" ]; then
    echo -e "${GREEN}  ✓ JSON field '.${field}' = '$expected' - $message${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}  ✗ JSON field '.${field}' = '$value' (expected '$expected') - $message${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# Test 1: User Registration
print_header "TEST SUITE 1: User Registration & Authentication"

test_case "User Registration"
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"$TEST_USER_PASSWORD\",
    \"name\": \"$TEST_USER_NAME\"
  }")

assert_status "$REGISTER_RESPONSE" "201" "User registration should succeed"
REGISTER_JSON=$(echo "$REGISTER_RESPONSE" | head -n -1)

test_case "User Login"
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"$TEST_USER_PASSWORD\"
  }")

assert_status "$LOGIN_RESPONSE" "200" "User login should succeed"
LOGIN_JSON=$(echo "$LOGIN_RESPONSE" | head -n -1)

# Extract tokens
ACCESS_TOKEN=$(echo "$LOGIN_JSON" | jq -r '.access' 2>/dev/null)
REFRESH_TOKEN=$(echo "$LOGIN_JSON" | jq -r '.refresh' 2>/dev/null)

echo -e "${GREEN}  Tokens obtained: access=$ACCESS_TOKEN refresh=$REFRESH_TOKEN${NC}"

test_case "Invalid Login Attempt"
INVALID_LOGIN=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"WrongPassword\"
  }")

assert_status "$INVALID_LOGIN" "401" "Invalid credentials should be rejected"

echo ""

# Test 2: User Profile
print_header "TEST SUITE 2: User Profile Management"

test_case "Get Current User Profile"
PROFILE_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/users/me/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$PROFILE_RESPONSE" "200" "Should retrieve current user profile"
PROFILE_JSON=$(echo "$PROFILE_RESPONSE" | head -n -1)
assert_json "$PROFILE_JSON" "email" "$TEST_USER_EMAIL" "Email should match"

test_case "Update User Profile"
UPDATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X PATCH "$API_URL/users/me/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Updated Name\",
    \"phone\": \"+1234567890\"
  }")

assert_status "$UPDATE_RESPONSE" "200" "Profile update should succeed"

echo ""

# Test 3: Donation Creation & Management
print_header "TEST SUITE 3: Donation Management"

test_case "Create Donation"
DONATION_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/donations/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"food_name\": \"Fresh Tomatoes\",
    \"quantity\": \"50 kg\",
    \"categories\": [\"vegetables\"],
    \"urgency\": \"medium\",
    \"expiry_date\": \"2024-01-20\",
    \"location\": {
      \"latitude\": 40.7128,
      \"longitude\": -74.0060,
      \"address\": \"123 Main St, New York, NY\"
    }
  }")

assert_status "$DONATION_RESPONSE" "201" "Donation creation should succeed"
DONATION_JSON=$(echo "$DONATION_RESPONSE" | head -n -1)
DONATION_ID=$(echo "$DONATION_JSON" | jq -r '.id' 2>/dev/null)

echo -e "${GREEN}  Donation ID: $DONATION_ID${NC}"

test_case "Get Donation Details"
GET_DONATION=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/donations/$DONATION_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$GET_DONATION" "200" "Should retrieve donation details"
assert_json "$(echo "$GET_DONATION" | head -n -1)" "food_name" "Fresh Tomatoes" "Food name should match"

test_case "List All Donations"
LIST_DONATIONS=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/donations/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$LIST_DONATIONS" "200" "Should list all donations"
assert_contains "$(echo "$LIST_DONATIONS" | head -n -1)" "Fresh Tomatoes" "List should contain created donation"

test_case "Update Donation"
UPDATE_DONATION=$(curl -s -w "\n%{http_code}" -X PATCH "$API_URL/donations/$DONATION_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"quantity\": \"75 kg\"
  }")

assert_status "$UPDATE_DONATION" "200" "Donation update should succeed"

echo ""

# Test 4: Geolocation Services
print_header "TEST SUITE 4: Geolocation Services"

test_case "Calculate Distance"
DISTANCE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/geo/distance/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"lat1\": 40.7128,
    \"lon1\": -74.0060,
    \"lat2\": 40.7580,
    \"lon2\": -73.9855
  }")

assert_status "$DISTANCE_RESPONSE" "200" "Distance calculation should succeed"
DISTANCE_JSON=$(echo "$DISTANCE_RESPONSE" | head -n -1)
assert_contains "$DISTANCE_JSON" "distance" "Response should contain distance"

test_case "Find Nearby Donations"
NEARBY_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/donations/nearby/?lat=40.7128&lon=-74.0060&radius=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$NEARBY_RESPONSE" "200" "Should find nearby donations"

echo ""

# Test 5: Donation Claiming Workflow
print_header "TEST SUITE 5: Donation Claiming & Transfer"

# Create another test user for claiming
test_case "Create Second Test User"
CLAIMANT_EMAIL="claimant-$(date +%s)@example.com"
curl -s -X POST "$API_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$CLAIMANT_EMAIL\",
    \"password\": \"$TEST_USER_PASSWORD\",
    \"name\": \"Claimant User\"
  }" > /dev/null

LOGIN_CLAIMANT=$(curl -s -X POST "$API_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$CLAIMANT_EMAIL\",
    \"password\": \"$TEST_USER_PASSWORD\"
  }")

CLAIMANT_TOKEN=$(echo "$LOGIN_CLAIMANT" | jq -r '.access' 2>/dev/null)
echo -e "${GREEN}  ✓ Claimant user created${NC}"
TESTS_PASSED=$((TESTS_PASSED + 1))

test_case "Claim Donation"
CLAIM_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/donations/$DONATION_ID/claim/" \
  -H "Authorization: Bearer $CLAIMANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"notes\": \"Needed for food bank\"
  }")

assert_status "$CLAIM_RESPONSE" "200" "Donation claiming should succeed"
CLAIM_JSON=$(echo "$CLAIM_RESPONSE" | head -n -1)
assert_json "$CLAIM_JSON" "status" "claimed" "Donation status should be 'claimed'"

test_case "Cannot Claim Already Claimed Donation"
DOUBLE_CLAIM=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/donations/$DONATION_ID/claim/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{}")

assert_status "$DOUBLE_CLAIM" "400" "Should not allow double claiming"

echo ""

# Test 6: Analytics & Metrics
print_header "TEST SUITE 6: Analytics & Impact Metrics"

test_case "Get Analytics Dashboard"
ANALYTICS=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/analytics/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$ANALYTICS" "200" "Should retrieve analytics"

test_case "Get Impact Metrics"
METRICS=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/analytics/impact-metrics/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$METRICS" "200" "Should retrieve impact metrics"

echo ""

# Test 7: Food Requests
print_header "TEST SUITE 7: Food Request Management"

test_case "Create Food Request"
REQUEST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/food-requests/" \
  -H "Authorization: Bearer $CLAIMANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"food_type\": \"vegetables\",
    \"quantity\": \"10 kg\",
    \"urgency\": \"high\",
    \"location\": {
      \"latitude\": 40.7580,
      \"longitude\": -73.9855,
      \"address\": \"456 Park Ave, New York, NY\"
    }
  }")

assert_status "$REQUEST_RESPONSE" "201" "Food request creation should succeed"
REQUEST_JSON=$(echo "$REQUEST_RESPONSE" | head -n -1)
REQUEST_ID=$(echo "$REQUEST_JSON" | jq -r '.id' 2>/dev/null)

test_case "List Food Requests"
LIST_REQUESTS=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/food-requests/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$LIST_REQUESTS" "200" "Should list food requests"

echo ""

# Test 8: Token Refresh
print_header "TEST SUITE 8: Token Management"

test_case "Refresh Access Token"
REFRESH_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh\": \"$REFRESH_TOKEN\"
  }")

assert_status "$REFRESH_RESPONSE" "200" "Token refresh should succeed"
NEW_TOKEN=$(echo "$REFRESH_RESPONSE" | head -n -1 | jq -r '.access' 2>/dev/null)

test_case "Use Refreshed Token"
VERIFY_NEW_TOKEN=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/users/me/" \
  -H "Authorization: Bearer $NEW_TOKEN")

assert_status "$VERIFY_NEW_TOKEN" "200" "Refreshed token should work"

echo ""

# Test 9: Error Handling
print_header "TEST SUITE 9: Error Handling"

test_case "Unauthorized Access"
UNAUTHORIZED=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/donations/")

assert_status "$UNAUTHORIZED" "401" "Requests without token should be rejected"

test_case "Not Found Error"
NOT_FOUND=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/donations/nonexistent-id/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$NOT_FOUND" "404" "Should return 404 for non-existent resource"

test_case "Invalid Request Data"
INVALID_DATA=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/donations/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"food_name\": \"\"
  }")

assert_status "$INVALID_DATA" "400" "Should reject invalid data"

echo ""

# Test 10: Cleanup & Deletion
print_header "TEST SUITE 10: Resource Deletion"

test_case "Delete Donation"
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL/donations/$DONATION_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$DELETE_RESPONSE" "204" "Donation deletion should succeed"

test_case "Verify Donation Deleted"
VERIFY_DELETE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/donations/$DONATION_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

assert_status "$VERIFY_DELETE" "404" "Deleted donation should not be found"

echo ""

# Final Summary
print_header "TEST EXECUTION SUMMARY"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo -e "Total Tests Run:    ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Tests Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:       ${RED}$TESTS_FAILED${NC}"
echo -e "Pass Rate:          ${BLUE}${PASS_RATE}%${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║ ✓ ALL TESTS PASSED - SYSTEM OPERATIONAL                   ║${NC}"
  echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
  exit 0
else
  echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
  echo -e "${RED}║ ✗ SOME TESTS FAILED - REVIEW ERRORS ABOVE                 ║${NC}"
  echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
  exit 1
fi
