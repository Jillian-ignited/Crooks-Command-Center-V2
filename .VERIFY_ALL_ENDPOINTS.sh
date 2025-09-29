#!/bin/bash
# Comprehensive Endpoint Verification Script for Crooks Command Center V2
# This script verifies all endpoints and ensures they match the frontend

# Configuration
BASE_URL="https://crooks-command-center-v2.onrender.com"
OUTPUT_DIR="endpoint_verification"
CURL_TIMEOUT=5

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    local url="${BASE_URL}${endpoint}"
    local output_file="${OUTPUT_DIR}/$(echo ${endpoint} | tr '/' '_' | sed 's/^_//')"
    
    echo -e "${YELLOW}Testing: ${endpoint}${NC}"
    
    # Make the request and capture response
    HTTP_CODE=$(curl -s -o "${output_file}.json" -w "%{http_code}" -m $CURL_TIMEOUT "$url")
    
    # Check if the request was successful
    if [[ $HTTP_CODE -ge 200 && $HTTP_CODE -lt 300 ]]; then
        echo -e "${GREEN}✓ ${endpoint} - ${HTTP_CODE}${NC}"
        echo "$endpoint" >> "${OUTPUT_DIR}/successful_endpoints.txt"
        return 0
    else
        echo -e "${RED}✗ ${endpoint} - ${HTTP_CODE}${NC}"
        echo "$endpoint" >> "${OUTPUT_DIR}/failed_endpoints.txt"
        return 1
    fi
}

# Function to analyze HTML for API calls
analyze_html() {
    local html_file=$1
    local output_file="${OUTPUT_DIR}/frontend_api_calls.txt"
    
    echo "Analyzing HTML file: $html_file"
    
    # Extract API calls using grep
    grep -o '"/api/[^"]*"' "$html_file" | tr -d '"' >> "$output_file"
    grep -o "'/api/[^']*'" "$html_file" | tr -d "'" >> "$output_file"
    grep -o '"/[^"]*"' "$html_file" | grep -v '"/api/' | tr -d '"' | grep -v '^"/static/' >> "$output_file"
    grep -o "'/[^']*'" "$html_file" | grep -v "'/api/" | tr -d "'" | grep -v "^'/static/" >> "$output_file"
    
    # Remove duplicates
    sort "$output_file" | uniq > "${output_file}.tmp"
    mv "${output_file}.tmp" "$output_file"
    
    echo "Found $(wc -l < "$output_file") unique API calls in frontend"
}

# Clear previous results
rm -f "${OUTPUT_DIR}/successful_endpoints.txt" "${OUTPUT_DIR}/failed_endpoints.txt" "${OUTPUT_DIR}/frontend_api_calls.txt"

# Test system endpoints
echo -e "\n${YELLOW}Testing system endpoints...${NC}"
test_endpoint "/api/status"
test_endpoint "/api/health"
test_endpoint "/api/routes"

# Test intelligence endpoints
echo -e "\n${YELLOW}Testing intelligence endpoints...${NC}"
test_endpoint "/api/intelligence"
test_endpoint "/api/intelligence/"
test_endpoint "/api/intelligence/dashboard"
test_endpoint "/api/intelligence/report"
test_endpoint "/api/intelligence/summary"
test_endpoint "/api/intelligence/competitors"

# Test content endpoints
echo -e "\n${YELLOW}Testing content endpoints...${NC}"
test_endpoint "/api/content"
test_endpoint "/api/content/"
test_endpoint "/api/content/dashboard"
test_endpoint "/api/content/ideas/generate"
test_endpoint "/api/content/calendar"
test_endpoint "/api/content/analytics"

# Test agency endpoints
echo -e "\n${YELLOW}Testing agency endpoints...${NC}"
test_endpoint "/api/agency"
test_endpoint "/api/agency/"
test_endpoint "/api/agency/dashboard"
test_endpoint "/api/agency/projects"
test_endpoint "/api/agency/deliverables"
test_endpoint "/api/agency/metrics"

# Test executive endpoints
echo -e "\n${YELLOW}Testing executive endpoints...${NC}"
test_endpoint "/api/executive"
test_endpoint "/api/executive/"
test_endpoint "/api/executive/overview"
test_endpoint "/api/executive/kpis"
test_endpoint "/api/executive/reports"

# Test calendar endpoints
echo -e "\n${YELLOW}Testing calendar endpoints...${NC}"
test_endpoint "/api/calendar"
test_endpoint "/api/calendar/"
test_endpoint "/api/calendar/upcoming"
test_endpoint "/api/calendar/events"
test_endpoint "/api/calendar/schedule"

# Test media endpoints
echo -e "\n${YELLOW}Testing media endpoints...${NC}"
test_endpoint "/api/media"
test_endpoint "/api/media/"
test_endpoint "/api/media/library"
test_endpoint "/api/media/analytics"

# Test shopify endpoints
echo -e "\n${YELLOW}Testing shopify endpoints...${NC}"
test_endpoint "/api/shopify"
test_endpoint "/api/shopify/"
test_endpoint "/api/shopify/analytics"
test_endpoint "/api/shopify/products"
test_endpoint "/api/shopify/orders"
test_endpoint "/api/shopify/customers"

# Test summary endpoints
echo -e "\n${YELLOW}Testing summary endpoints...${NC}"
test_endpoint "/api/summary"
test_endpoint "/api/summary/"
test_endpoint "/api/summary/dashboard"
test_endpoint "/api/summary/performance"
test_endpoint "/api/summary/insights"

# Test ingest endpoints
echo -e "\n${YELLOW}Testing ingest endpoints...${NC}"
test_endpoint "/api/ingest"
test_endpoint "/api/ingest/"
test_endpoint "/api/ingest/overview"

# Test upload endpoints
echo -e "\n${YELLOW}Testing upload endpoints...${NC}"
test_endpoint "/api/upload"
test_endpoint "/api/upload/"
test_endpoint "/api/upload/history"

# Test non-API endpoints (should be forwarded to API)
echo -e "\n${YELLOW}Testing non-API endpoints (should be forwarded)...${NC}"
test_endpoint "/intelligence/dashboard"
test_endpoint "/content/dashboard"
test_endpoint "/agency/dashboard"
test_endpoint "/executive/overview"
test_endpoint "/calendar/upcoming"
test_endpoint "/media/library"
test_endpoint "/shopify/analytics"
test_endpoint "/summary/dashboard"
test_endpoint "/ingest/overview"

# Download and analyze the frontend HTML
echo -e "\n${YELLOW}Downloading and analyzing frontend HTML...${NC}"
curl -s -o "${OUTPUT_DIR}/index.html" "${BASE_URL}"
analyze_html "${OUTPUT_DIR}/index.html"

# Compare frontend API calls with successful endpoints
echo -e "\n${YELLOW}Comparing frontend API calls with successful endpoints...${NC}"
if [ -f "${OUTPUT_DIR}/frontend_api_calls.txt" ] && [ -f "${OUTPUT_DIR}/successful_endpoints.txt" ]; then
    # Find API calls that don't have a successful endpoint
    grep -v -f "${OUTPUT_DIR}/successful_endpoints.txt" "${OUTPUT_DIR}/frontend_api_calls.txt" > "${OUTPUT_DIR}/missing_endpoints.txt"
    
    # Count results
    SUCCESSFUL_COUNT=$(wc -l < "${OUTPUT_DIR}/successful_endpoints.txt")
    FAILED_COUNT=$(wc -l < "${OUTPUT_DIR}/failed_endpoints.txt")
    FRONTEND_CALLS_COUNT=$(wc -l < "${OUTPUT_DIR}/frontend_api_calls.txt")
    MISSING_COUNT=$(wc -l < "${OUTPUT_DIR}/missing_endpoints.txt")
    
    # Print summary
    echo -e "\n${YELLOW}=== ENDPOINT VERIFICATION SUMMARY ===${NC}"
    echo -e "${GREEN}Successful endpoints: ${SUCCESSFUL_COUNT}${NC}"
    echo -e "${RED}Failed endpoints: ${FAILED_COUNT}${NC}"
    echo -e "${YELLOW}Frontend API calls: ${FRONTEND_CALLS_COUNT}${NC}"
    echo -e "${RED}Missing endpoints: ${MISSING_COUNT}${NC}"
    
    # Print missing endpoints
    if [ $MISSING_COUNT -gt 0 ]; then
        echo -e "\n${RED}Missing endpoints that frontend is trying to access:${NC}"
        cat "${OUTPUT_DIR}/missing_endpoints.txt"
    fi
else
    echo -e "${RED}Could not compare frontend API calls with endpoints${NC}"
fi

echo -e "\n${YELLOW}Verification complete! Results saved to ${OUTPUT_DIR}/${NC}"

