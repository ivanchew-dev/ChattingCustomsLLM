# ChattingCustoms LLM

AI-powered chatbot system for Singapore customs and trade-related queries with threat assessment capabilities.

## Quick Start

### Automated Setup (Recommended)
```bash
# Run the automated setup script
./setup.sh
```

### Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp dev.env.example dev.env
# Edit dev.env and add your OpenAI API key

# 4. Run the application
cd src/chattingcustoms
streamlit run main.py
```

## Features

- **Multi-Bot Architecture**: Self-service trader, expert trader, TNO compliance, and threat assessment bots
- **Interactive UI**: Streamlit-based chat interface with data visualization
- **Security Monitoring**: Real-time threat detection and geolocation tracking
- **RAG Integration**: Vector database with ChromaDB for knowledge retrieval

## Requirements

- Python 3.8+
- OpenAI API key
- See `requirements.txt` for full dependency list

## Project Structure

```
├── requirements.txt          # Python dependencies
├── setup.sh                 # Automated setup script
├── SETUP.md                 # Detailed setup guide
├── src/chattingcustoms/     # Main application
├── datastore/               # Data files
└── vector_db/               # ChromaDB storage
```

## Documentation

- **[SETUP.md](SETUP.md)** - Comprehensive setup guide with troubleshooting
- **[requirements.txt](requirements.txt)** - Python dependencies
- **Default Login**: admin / secure

## Usage

1. Run setup: `./setup.sh`
2. Configure API key in `dev.env`
3. Start app: `cd src/chattingcustoms && streamlit run main.py`
4. Open browser: http://localhost:8501

## Support

For setup issues, see [SETUP.md](SETUP.md) troubleshooting section.