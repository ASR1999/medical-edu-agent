#!/bin/bash
# 🚀 Complete Setup and Startup Script for Medical AI Agent
# This script will guide you through the complete setup process

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "    🩺 MEDICAL AI AGENT - COMPLETE SETUP"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="/home/uwcuser/nltk_data/mtech-medical-agent"

# Check if we're in the right directory
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Project directory not found at $PROJECT_ROOT${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

echo "📁 Working directory: $(pwd)"
echo ""

# =====================================================
# STEP 1: Check Prerequisites
# =====================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 1: Checking Prerequisites${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python: $PYTHON_VERSION"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js: $NODE_VERSION"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker: $DOCKER_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Docker not found (optional for containerized setup)"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose: $COMPOSE_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Docker Compose not found (optional)"
fi

echo ""

# =====================================================
# STEP 2: Setup Environment Files
# =====================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 2: Setting Up Environment Files${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Backend .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠${NC} backend/.env not found. Creating from template..."
    cp backend/ENV_EXAMPLE backend/.env
    echo -e "${GREEN}✓${NC} Created backend/.env"
    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: You need to edit backend/.env and add your API keys:${NC}"
    echo "   - GROQ_API_KEY"
    echo "   - SERPER_API_KEY"
    echo ""
    read -p "Press Enter after you've added your API keys to backend/.env..."
else
    echo -e "${GREEN}✓${NC} backend/.env already exists"
fi

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}⚠${NC} frontend/.env not found. Creating..."
    echo "VITE_API_URL=http://localhost:8000/api" > frontend/.env
    echo -e "${GREEN}✓${NC} Created frontend/.env"
else
    echo -e "${GREEN}✓${NC} frontend/.env already exists"
fi

echo ""

# =====================================================
# STEP 3: Convert ASR Model to CT2
# =====================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 3: Converting ASR Model to CTranslate2${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

CT2_MODEL_PATH="backend/ct2_models/medasr-v2-ct2"

if [ -d "$CT2_MODEL_PATH" ] && [ -f "$CT2_MODEL_PATH/model.bin" ]; then
    echo -e "${GREEN}✓${NC} CT2 model already exists at $CT2_MODEL_PATH"
else
    echo -e "${YELLOW}⚠${NC} CT2 model not found. Converting..."
    
    # Check if source model exists
    if [ ! -d "medasr-v2" ]; then
        echo -e "${RED}✗ Source model 'medasr-v2' not found${NC}"
        echo "   Please ensure your fine-tuned Whisper model is at: medasr-v2/"
        exit 1
    fi
    
    cd ml-training
    
    # Install required packages
    echo "Installing conversion dependencies..."
    pip install -q ctranslate2>=3.20.0 transformers>=4.35.0 torch
    
    # Run conversion
    echo "Running conversion (this may take a few minutes)..."
    ./convert_to_ct2.sh
    
    cd ..
    
    if [ -f "$CT2_MODEL_PATH/model.bin" ]; then
        echo -e "${GREEN}✓${NC} CT2 model conversion successful!"
    else
        echo -e "${RED}✗ CT2 model conversion failed${NC}"
        exit 1
    fi
fi

echo ""

# =====================================================
# STEP 4: Choose Setup Method
# =====================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 4: Choose Setup Method${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Choose how you want to run the application:"
echo ""
echo "  1) Docker Compose (Recommended - Easiest)"
echo "  2) Local Development (Backend + Frontend separately)"
echo "  3) Exit and setup manually"
echo ""

read -p "Enter choice [1-3]: " SETUP_CHOICE

case $SETUP_CHOICE in
    1)
        # =====================================================
        # DOCKER COMPOSE SETUP
        # =====================================================
        echo ""
        echo -e "${GREEN}🐳 Starting with Docker Compose...${NC}"
        echo ""
        
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}✗ Docker Compose not found${NC}"
            exit 1
        fi
        
        echo "Building and starting services..."
        docker-compose up --build -d
        
        echo ""
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}    ✅ DOCKER SETUP COMPLETE!${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo "🌐 Access the application at:"
        echo ""
        echo "   Frontend:  http://localhost:5173"
        echo "   Backend:   http://localhost:8000/api"
        echo "   API Docs:  http://localhost:8000/docs"
        echo "   FHIR:      http://localhost:8080/fhir"
        echo ""
        echo "📋 Useful commands:"
        echo ""
        echo "   View logs:      docker-compose logs -f"
        echo "   Stop services:  docker-compose down"
        echo "   Restart:        docker-compose restart"
        echo ""
        ;;
        
    2)
        # =====================================================
        # LOCAL DEVELOPMENT SETUP
        # =====================================================
        echo ""
        echo -e "${GREEN}💻 Setting up Local Development...${NC}"
        echo ""
        
        # Backend setup
        echo -e "${YELLOW}Setting up Backend...${NC}"
        cd backend
        
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        echo "Activating virtual environment..."
        source venv/bin/activate
        
        echo "Installing dependencies..."
        pip install -q -r requirements.txt
        
        cd ..
        
        # Frontend setup
        echo ""
        echo -e "${YELLOW}Setting up Frontend...${NC}"
        cd frontend
        
        if [ ! -d "node_modules" ]; then
            echo "Installing npm packages..."
            npm install
        fi
        
        cd ..
        
        echo ""
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}    ✅ LOCAL SETUP COMPLETE!${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo "🚀 To start the application, run in 3 separate terminals:"
        echo ""
        echo "Terminal 1 (Backend):"
        echo "   cd $PROJECT_ROOT/backend"
        echo "   source venv/bin/activate"
        echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        echo ""
        echo "Terminal 2 (Frontend):"
        echo "   cd $PROJECT_ROOT/frontend"
        echo "   npm run dev"
        echo ""
        echo "Terminal 3 (FHIR Server - Optional):"
        echo "   docker run -p 8080:8080 hapiproject/hapi:latest"
        echo ""
        echo "Then access:"
        echo "   Frontend:  http://localhost:5173"
        echo "   Backend:   http://localhost:8000/api"
        echo "   API Docs:  http://localhost:8000/docs"
        echo ""
        ;;
        
    3)
        echo ""
        echo "Setup cancelled. Please refer to QUICK_START.md for manual setup."
        echo ""
        exit 0
        ;;
        
    *)
        echo ""
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        echo ""
        exit 1
        ;;
esac

# =====================================================
# STEP 5: Test the System (Optional)
# =====================================================
echo ""
read -p "Would you like to run integration tests? (y/n): " RUN_TESTS

if [ "$RUN_TESTS" = "y" ] || [ "$RUN_TESTS" = "Y" ]; then
    echo ""
    echo -e "${BLUE}Running integration tests...${NC}"
    echo ""
    
    # Wait a bit for services to be fully up
    echo "Waiting 10 seconds for services to start..."
    sleep 10
    
    cd scripts
    python test_integration.py
    cd ..
fi

# =====================================================
# FINAL INSTRUCTIONS
# =====================================================
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    🎉 SETUP COMPLETE - SYSTEM READY!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📚 Next Steps:"
echo ""
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Select a patient from the dropdown"
echo "   3. Try asking: 'What medications am I taking?'"
echo "   4. Try voice input by clicking the microphone"
echo "   5. Upload a medical image to test vision analysis"
echo ""
echo "📖 Documentation:"
echo ""
echo "   QUICK_START.md    - Quick setup guide"
echo "   README.md         - Full documentation"
echo "   TESTING_GUIDE.md  - Testing instructions"
echo "   SUMMARY.md        - Implementation summary"
echo ""
echo "🐛 Troubleshooting:"
echo ""
echo "   - View logs: docker-compose logs -f (Docker) or check terminal output"
echo "   - Test API: curl http://localhost:8000/api/hello"
echo "   - Run tests: python scripts/test_integration.py"
echo ""
echo "Happy coding! 🚀"
echo ""




