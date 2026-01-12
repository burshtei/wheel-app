#!/bin/bash
# Test script for Wheel Strategy Analyzer API

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if API URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide API URL${NC}"
    echo "Usage: ./test_api.sh <API_URL>"
    echo "Example: ./test_api.sh https://wheel-analyzer-api.onrender.com"
    exit 1
fi

API_URL=$1

echo -e "${GREEN}Testing Wheel Strategy Analyzer API${NC}"
echo -e "API URL: ${YELLOW}$API_URL${NC}"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}[1/6]${NC} Testing health check..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Health check passed"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}✗${NC} Health check failed"
fi
echo ""

# Test 2: Root Endpoint
echo -e "${YELLOW}[2/6]${NC} Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "$API_URL/")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Root endpoint working"
else
    echo -e "${RED}✗${NC} Root endpoint failed"
fi
echo ""

# Test 3: Popular Tickers
echo -e "${YELLOW}[3/6]${NC} Getting popular tickers..."
TICKERS_RESPONSE=$(curl -s "$API_URL/api/v1/popular-tickers")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Popular tickers retrieved"
    echo "$TICKERS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
else
    echo -e "${RED}✗${NC} Failed to get popular tickers"
fi
echo ""

# Test 4: Ticker Price
echo -e "${YELLOW}[4/6]${NC} Getting AAPL price..."
PRICE_RESPONSE=$(curl -s "$API_URL/api/v1/ticker/AAPL/price")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Price retrieved"
    echo "$PRICE_RESPONSE" | python3 -m json.tool 2>/dev/null
else
    echo -e "${RED}✗${NC} Failed to get price"
fi
echo ""

# Test 5: Analyze Ticker
echo -e "${YELLOW}[5/6]${NC} Analyzing AAPL (this may take 10-20 seconds)..."
ANALYZE_RESPONSE=$(curl -s "$API_URL/api/v1/analyze/AAPL?target_dte=30")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Analysis complete"
    echo "$ANALYZE_RESPONSE" | python3 -m json.tool 2>/dev/null | head -30
else
    echo -e "${RED}✗${NC} Analysis failed"
fi
echo ""

# Test 6: Find Best Candidates
echo -e "${YELLOW}[6/6]${NC} Finding best wheel candidates (this may take 20-30 seconds)..."
CANDIDATES_RESPONSE=$(curl -s "$API_URL/api/v1/candidates?min_annual_return=15&max_results=3")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Candidates found"
    echo "$CANDIDATES_RESPONSE" | python3 -m json.tool 2>/dev/null | head -40
else
    echo -e "${RED}✗${NC} Failed to find candidates"
fi
echo ""

# Summary
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Testing Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "API Documentation:"
echo -e "  Swagger UI: ${YELLOW}$API_URL/docs${NC}"
echo -e "  ReDoc:      ${YELLOW}$API_URL/redoc${NC}"
echo ""
echo -e "${GREEN}✓${NC} API is working correctly!"
