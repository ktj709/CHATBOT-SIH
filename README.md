# GyaanSetu RAG Chatbot

A Python-based RAG (Retrieval-Augmented Generation) chatbot for the GyaanSetu education platform. Uses TF-IDF for lightweight retrieval and Gemini 2.0 Flash for response generation.

## Features

- 🔍 **Smart Retrieval**: TF-IDF based semantic search on knowledge base
- 🤖 **Gemini 2.0 Flash**: Fast, accurate responses
- 💬 **Conversation History**: Maintains context across turns
- 🌐 **Web Interface**: Modern dark-themed chat UI
- 🚀 **Render Ready**: Deploy with one click

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_api_key_here
```

### 3. Run Locally

**CLI Mode:**
```bash
python main.py
```

**Web Interface:**
```bash
python app.py
# Visit http://localhost:5000
```

## Deploy to Render

1. Push this repo to GitHub
2. Connect to [Render](https://render.com)
3. Create a new **Web Service**
4. Set environment variable: `GEMINI_API_KEY`
5. Render will auto-detect the `Procfile` and deploy

## Project Structure

```
├── app.py                 # Flask web application
├── main.py                # CLI interface
├── chatbot.py             # Core chatbot logic
├── retriever.py           # TF-IDF retrieval
├── knowledge_processor.py # JSON to chunks processor
├── config.py              # Configuration
├── knowledge_base.json    # Knowledge base data
├── requirements.txt       # Python dependencies
├── Procfile              # Render/Gunicorn config
└── .env                  # Environment variables (gitignored)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Chat web interface |
| `/chat` | POST | Send message, get response |
| `/health` | GET | Health check |
| `/clear` | POST | Clear conversation |

## Example Usage

```python
from chatbot import get_chatbot

bot = get_chatbot()
response = bot.chat("What is GyaanSetu?")
print(response)
```

## License

MIT
