# ChattingCustoms LLM Setup Guide

## Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Git (optional, for version control)

## Step-by-Step Setup

### 1. Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd ChattingCustomsLLM

# Or download and extract the ZIP file
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Alternative: Install packages individually if requirements.txt fails
pip install streamlit pandas openai python-dotenv altair
pip install langchain langchain-openai langchain-community langchain-experimental langchain-core
pip install chromadb geoip2 requests
```

### 4. Environment Configuration

#### Create Environment Files
Create the following environment files in the root directory:

**dev.env** (for development):
```bash
OPENAI_API_KEY=your_openai_api_key_here
environment=dev
```

**prod.env** (for production):
```bash
OPENAI_API_KEY=your_openai_api_key_here
environment=prod
```

#### Get OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key and paste it in your environment files

### 5. Data Setup

#### Required Data Files
Ensure these files exist in the correct locations:

**Threat Data**:
- `datastore/appData/threatData.csv` - Contains threat monitoring data
- If missing, the app will still run but without threat visualization

**GeoIP Database**:
- `datastore/ragData/GeoLite2-City.mmdb` - For IP geolocation
- Download from [MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) (free account required)

**Knowledge Base**:
- `datastore/ragData/*.txt` - Text files for RAG functionality
- These should contain customs/trade-related information

### 6. Streamlit Configuration (Optional)

The app includes a Streamlit theme configuration at:
`src/chattingcustoms/.streamlit/config.toml`

You can customize the appearance by editing this file.

### 7. Run the Application

#### Navigate to the Source Directory
```bash
cd src/chattingcustoms
```

#### Run the Main Application
```bash
streamlit run main.py
```

The application will open in your browser at `http://localhost:8501`

### 8. Test the Setup

#### Login Credentials
- Username: `admin`
- Password: `secure`

#### Test Features
1. **Chat Interface**: Ask questions about Singapore customs
2. **Threat Data Viewer**: View security monitoring dashboard
3. **RAG Functionality**: Test knowledge base queries

## Project Structure
```
ChattingCustomsLLM/
├── requirements.txt          # Python dependencies
├── dev.env                  # Development environment variables
├── prod.env                 # Production environment variables
├── src/chattingcustoms/     # Main application code
│   ├── main.py             # Main Streamlit app
│   ├── core/               # Chatbot implementations
│   ├── helper/             # Utility functions
│   └── .streamlit/         # Streamlit configuration
├── datastore/              # Data files
│   ├── appData/           # Application data
│   └── ragData/           # RAG knowledge base
└── vector_db/             # ChromaDB vector storage
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# If you get import errors, ensure you're in the right directory
cd src/chattingcustoms
python -c "import streamlit; print('Streamlit installed successfully')"
```

#### API Key Issues
```bash
# Test your OpenAI API key
python -c "
from helper import key_util
print('API Key loaded:', key_util.return_open_api_key()[:10] + '...')
"
```

#### Missing Data Files
- The app will run without `threatData.csv` but threat visualization won't work
- Without `GeoLite2-City.mmdb`, geolocation features will be disabled
- RAG functionality requires text files in `datastore/ragData/`

#### Port Already in Use
```bash
# Run on a different port
streamlit run main.py --server.port 8502
```

#### Package Version Conflicts
```bash
# Create a fresh virtual environment
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Virtual Environment Issues

#### Activation Problems
```bash
# On macOS/Linux - if source doesn't work
. .venv/bin/activate

# On Windows - if Scripts doesn't work
.venv\bin\activate
```

#### Permission Issues (macOS/Linux)
```bash
chmod +x .venv/bin/activate
```

### Performance Issues

#### Large Vector Database
- The ChromaDB database in `vector_db/` can become large
- Delete and regenerate if experiencing performance issues

#### Memory Usage
- Streamlit can use significant memory with large datasets
- Consider reducing the size of `threatData.csv` for testing

## Development Mode

#### Install Development Dependencies
```bash
pip install jupyter notebook ipython
```

#### Environment Variables
- Set `environment=dev` in your environment file
- This enables development-specific features

## Production Deployment

#### Environment Setup
```bash
# Use production environment
export environment=prod
# or set in prod.env file
```

#### Security Considerations
- Use strong credentials (not admin/secure)
- Protect API keys
- Consider IP whitelisting for production

## Support

#### Check Installation
```bash
# Verify all components
python -c "
import streamlit as st
import pandas as pd
import openai
import langchain
import chromadb
print('All core dependencies installed successfully!')
"
```

#### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

For additional help, check:
- Streamlit documentation: https://docs.streamlit.io/
- OpenAI API documentation: https://platform.openai.com/docs
- LangChain documentation: https://python.langchain.com/