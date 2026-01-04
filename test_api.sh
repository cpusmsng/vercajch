#!/bin/bash

# API Test Script for Vercajch
# Usage: ./test_api.sh [API_URL]
# Default API_URL: http://localhost:8000/api

API_URL="${1:-http://localhost:8000/api}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "  Vercajch API Test Script"
echo "  API URL: $API_URL"
echo "========================================"
echo ""

# Store tokens
ADMIN_TOKEN=""
MANAGER_TOKEN=""
LEADER_TOKEN=""
WORKER_TOKEN=""

passed=0
failed=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local token="$4"
    local expected_code="$5"
    local data="$6"

    local auth_header=""
    if [ -n "$token" ]; then
        auth_header="-H \"Authorization: Bearer $token\""
    fi

    local data_args=""
    if [ -n "$data" ]; then
        data_args="-d \"$data\""
    fi

    local response
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL$endpoint" -H "Authorization: Bearer $token" 2>/dev/null)
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d "$data" 2>/dev/null)
    fi

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    if [ "$http_code" == "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name (HTTP $http_code)"
        ((passed++))
        return 0
    else
        echo -e "${RED}✗${NC} $name (Expected: $expected_code, Got: $http_code)"
        echo "  Response: $(echo "$body" | head -c 200)"
        ((failed++))
        return 1
    fi
}

# Login and get tokens
echo "=== Authentication Tests ==="

# Admin login
response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@spp-d.sk&password=admin123")
ADMIN_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$ADMIN_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Admin login successful"
    ((passed++))
else
    echo -e "${RED}✗${NC} Admin login failed"
    echo "  Response: $response"
    ((failed++))
fi

# Manager login
response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=manager@spp-d.sk&password=manager123")
MANAGER_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$MANAGER_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Manager login successful"
    ((passed++))
else
    echo -e "${RED}✗${NC} Manager login failed"
    ((failed++))
fi

# Leader login
response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=leader@spp-d.sk&password=leader123")
LEADER_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$LEADER_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Leader login successful"
    ((passed++))
else
    echo -e "${RED}✗${NC} Leader login failed"
    ((failed++))
fi

# Worker login
response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=worker1@spp-d.sk&password=worker123")
WORKER_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$WORKER_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Worker login successful"
    ((passed++))
else
    echo -e "${RED}✗${NC} Worker login failed"
    ((failed++))
fi

echo ""
echo "=== User Endpoints ==="
test_endpoint "GET /users/departments" "GET" "/users/departments" "$WORKER_TOKEN" "200"
test_endpoint "GET /users/roles" "GET" "/users/roles" "$WORKER_TOKEN" "200"
test_endpoint "GET /users/team" "GET" "/users/team" "$LEADER_TOKEN" "200"

echo ""
echo "=== Equipment Endpoints ==="
test_endpoint "GET /equipment" "GET" "/equipment" "$WORKER_TOKEN" "200"
test_endpoint "GET /equipment/new" "GET" "/equipment/new" "$MANAGER_TOKEN" "200"
test_endpoint "GET /equipment/new/history" "GET" "/equipment/new/history" "$MANAGER_TOKEN" "200"

echo ""
echo "=== Categories & Locations ==="
test_endpoint "GET /categories" "GET" "/categories" "$WORKER_TOKEN" "200"
test_endpoint "GET /locations" "GET" "/locations" "$WORKER_TOKEN" "200"

echo ""
echo "=== Tags ==="
test_endpoint "GET /tags/lookup (not found)" "GET" "/tags/lookup?value=test-tag" "$WORKER_TOKEN" "200"

echo ""
echo "=== Calibrations ==="
test_endpoint "GET /calibrations/equipment/new" "GET" "/calibrations/equipment/new" "$WORKER_TOKEN" "200"
test_endpoint "GET /calibrations/dashboard" "GET" "/calibrations/dashboard" "$WORKER_TOKEN" "200"

echo ""
echo "=== Maintenance ==="
test_endpoint "GET /maintenance/stats" "GET" "/maintenance/stats" "$WORKER_TOKEN" "200"
test_endpoint "GET /maintenance" "GET" "/maintenance" "$WORKER_TOKEN" "200"

echo ""
echo "=== Transfers ==="
test_endpoint "GET /transfers/requests/sent" "GET" "/transfers/requests/sent" "$WORKER_TOKEN" "200"
test_endpoint "GET /transfers/requests/received" "GET" "/transfers/requests/received" "$WORKER_TOKEN" "200"
test_endpoint "GET /transfers/pending-approval (leader)" "GET" "/transfers/pending-approval" "$LEADER_TOKEN" "200"
test_endpoint "GET /transfers/pending-approval (worker - forbidden)" "GET" "/transfers/pending-approval" "$WORKER_TOKEN" "403"

echo ""
echo "=== Reports ==="
test_endpoint "GET /reports/equipment-summary" "GET" "/reports/equipment-summary" "$WORKER_TOKEN" "200"
test_endpoint "GET /reports/checkout-stats (leader)" "GET" "/reports/checkout-stats" "$LEADER_TOKEN" "200"
test_endpoint "GET /reports/checkout-stats (worker - forbidden)" "GET" "/reports/checkout-stats" "$WORKER_TOKEN" "403"

echo ""
echo "=== Settings ==="
test_endpoint "GET /settings" "GET" "/settings" "$WORKER_TOKEN" "200"
test_endpoint "GET /settings/public" "GET" "/settings/public" "" "200"

echo ""
echo "========================================"
echo "  Test Results"
echo "========================================"
echo -e "  ${GREEN}Passed: $passed${NC}"
echo -e "  ${RED}Failed: $failed${NC}"
echo "  Total: $((passed + failed))"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
