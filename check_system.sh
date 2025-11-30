#!/bin/bash
# 🔍 System Readiness Check for Medical AI Agent
# Run this before starting the system

echo "════════════════════════════════════════════════════════════"
echo "   🔍 MEDICAL AI AGENT - SYSTEM READINESS CHECK"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="/home/uwcuser/nltk_data/mtech-medical-agent"
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN_COUNT++))
}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Checking System Prerequisites${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    check_pass "Python: $VERSION"
else
    check_fail "Python 3 not found"
fi

# Check Node.js
if command -v node &> /dev/null; then
    VERSION=$(node --version)
    check_pass "Node.js: $VERSION"
else
    check_fail "Node.js not found"
fi

# Check npm
if command -v npm &> /dev/null; then
    VERSION=$(npm --version)
    check_pass "npm: $VERSION"
else
    check_fail "npm not found"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. Checking Project Files${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check backend .env
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    check_pass "Backend .env file exists"
    
    # Check for API keys
    if grep -q "GROQ_API_KEY=.\+" "$PROJECT_ROOT/backend/.env" 2>/dev/null; then
        check_pass "GROQ_API_KEY is set"
    else
        check_fail "GROQ_API_KEY is empty or missing"
    fi
    
    if grep -q "SERPER_API_KEY=.\+" "$PROJECT_ROOT/backend/.env" 2>/dev/null; then
        check_pass "SERPER_API_KEY is set"
    else
        check_warn "SERPER_API_KEY is empty (web search won't work)"
    fi
    
    if grep -q "OPENAI_API_KEY=.\+" "$PROJECT_ROOT/backend/.env" 2>/dev/null; then
        check_pass "OPENAI_API_KEY is set"
    else
        check_warn "OPENAI_API_KEY is empty (vision analysis won't work)"
    fi
else
    check_fail "Backend .env file not found"
    echo "         Run: cp backend/ENV_EXAMPLE backend/.env"
fi

# Check frontend .env
if [ -f "$PROJECT_ROOT/frontend/.env" ]; then
    check_pass "Frontend .env file exists"
else
    check_fail "Frontend .env file not found"
    echo "         Run: cp frontend/ENV_EXAMPLE frontend/.env"
fi

# Check ASR model
if [ -f "$PROJECT_ROOT/backend/ct2_models/medasr-v2-ct2/model.bin" ]; then
    SIZE=$(du -h "$PROJECT_ROOT/backend/ct2_models/medasr-v2-ct2/model.bin" | cut -f1)
    check_pass "ASR model exists ($SIZE)"
else
    check_fail "ASR model not found"
    echo "         Run: cd ml-training && ./convert_to_ct2.sh"
fi

# Check mock EHR data
if [ -f "$PROJECT_ROOT/backend/data/mock_ehr.json" ]; then
    PATIENT_COUNT=$(grep -o "patient_id_" "$PROJECT_ROOT/backend/data/mock_ehr.json" | wc -l)
    check_pass "Mock EHR data exists ($PATIENT_COUNT patients)"
else
    check_fail "Mock EHR data not found"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. Checking Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check backend dependencies
if [ -d "$PROJECT_ROOT/backend/venv" ] || python3 -c "import fastapi" 2>/dev/null; then
    check_pass "Backend dependencies (Python packages installed)"
else
    check_warn "Backend dependencies may not be installed"
    echo "         Run: cd backend && pip install -r requirements.txt"
fi

# Check frontend dependencies
if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    check_pass "Frontend dependencies (node_modules exists)"
else
    check_fail "Frontend dependencies not installed"
    echo "         Run: cd frontend && npm install"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. Checking Ports${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if ports are available
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    check_pass "Port 8000 (backend) is available"
else
    check_warn "Port 8000 is already in use"
    echo "         Backend may already be running, or run: pkill -f uvicorn"
fi

if ! lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    check_pass "Port 5173 (frontend) is available"
else
    check_warn "Port 5173 is already in use"
    echo "         Frontend may already be running, or run: pkill -f vite"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "   📊 SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✓ Passed:  $PASS_COUNT${NC}"
echo -e "${YELLOW}⚠ Warnings: $WARN_COUNT${NC}"
echo -e "${RED}✗ Failed:  $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ Your system is ready to run!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Terminal 1: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo "  2. Terminal 2: cd frontend && npm run dev"
    echo "  3. Open: http://localhost:5173"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Please fix the failed checks above before running.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  - Missing .env: cp backend/ENV_EXAMPLE backend/.env"
    echo "  - Add API keys: nano backend/.env"
    echo "  - Install backend deps: cd backend && pip install -r requirements.txt"
    echo "  - Install frontend deps: cd frontend && npm install"
    echo "  - Convert ASR model: cd ml-training && ./convert_to_ct2.sh"
    echo ""
    exit 1
fi




