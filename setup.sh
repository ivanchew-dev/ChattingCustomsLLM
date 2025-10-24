#!/bin/bash

# ChattingCustoms LLM Setup Script
# This script automates the setup process for the ChattingCustoms application

set -e  # Exit on any error

echo "🚀 ChattingCustoms LLM Setup Script"
echo "=================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi
echo "✅ Python version: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed from requirements.txt"
else
    echo "⚠️  requirements.txt not found. Installing core packages..."
    pip install streamlit pandas openai python-dotenv altair
    pip install langchain langchain-openai langchain-community langchain-experimental langchain-core
    pip install chromadb geoip2 requests
    echo "✅ Core dependencies installed"
fi

# Create environment files if they don't exist
echo "🔐 Setting up environment files..."

if [ ! -f "dev.env" ]; then
    cat > dev.env << EOF
# Development Environment Configuration
OPENAI_API_KEY=your_openai_api_key_here
environment=dev
EOF
    echo "✅ Created dev.env file"
else
    echo "⚠️  dev.env already exists"
fi

if [ ! -f "prod.env" ]; then
    cat > prod.env << EOF
# Production Environment Configuration
OPENAI_API_KEY=your_openai_api_key_here
environment=prod
EOF
    echo "✅ Created prod.env file"
else
    echo "⚠️  prod.env already exists"
fi

# Create data directories if they don't exist
echo "📁 Setting up data directories..."
mkdir -p datastore/appData
mkdir -p datastore/ragData
mkdir -p vector_db

# Create sample threat data if it doesn't exist
if [ ! -f "datastore/appData/threatData.csv" ]; then
    cat > datastore/appData/threatData.csv << EOF
query,ip_address,latitude,longitude,threat_category,threat_category_value,date,user
sample query,127.0.0.1,1.3521,103.8198,Sample,Low,2025-10-24 12:00:00,admin
EOF
    echo "✅ Created sample threatData.csv"
else
    echo "⚠️  threatData.csv already exists"
fi

# Create sample RAG data if directory is empty
if [ ! "$(ls -A datastore/ragData/*.txt 2>/dev/null)" ]; then
    cat > datastore/ragData/sample_customs_info.txt << EOF
Singapore Customs Information

Import Procedures:
1. Register as an importer with Singapore Customs
2. Obtain necessary permits and licenses
3. Submit import declaration
4. Pay duties and taxes
5. Arrange for cargo clearance

Export Procedures:
1. Register as an exporter with Singapore Customs  
2. Obtain export permits if required
3. Submit export declaration
4. Arrange for cargo inspection if needed
5. Complete export formalities

For more information, visit: https://www.customs.gov.sg
EOF
    echo "✅ Created sample RAG data file"
else
    echo "⚠️  RAG data files already exist"
fi

# Test installation
echo "🧪 Testing installation..."
cd src/chattingcustoms

python3 -c "
import streamlit as st
import pandas as pd  
import openai
try:
    import langchain
    import chromadb
    print('✅ All core dependencies imported successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Check if we can import local modules
python3 -c "
try:
    from helper import key_util, prompt_util
    from core import router
    print('✅ Local modules imported successfully!')
except ImportError as e:
    print(f'❌ Local module import error: {e}')
    print('This is normal if OpenAI API key is not configured yet.')
"

cd ../..

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. 📝 Edit dev.env and add your OpenAI API key"
echo "2. 📁 Add GeoLite2-City.mmdb to datastore/ragData/ (optional)"
echo "3. 📚 Add your knowledge base files to datastore/ragData/"
echo ""
echo "To run the application:"
echo "  source .venv/bin/activate"
echo "  cd src/chattingcustoms"
echo "  streamlit run main.py"
echo ""
echo "Default login: admin / secure"
echo "App URL: http://localhost:8501"
echo ""
echo "For detailed setup instructions, see SETUP.md"