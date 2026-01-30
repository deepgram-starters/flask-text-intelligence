# Flask Text Intelligence Starter

Text analysis demo using Deepgram's Text Intelligence API with Python Flask backend and web frontend.

## Prerequisites

- [Deepgram API Key](https://console.deepgram.com/signup?jump=keys) (sign up for free)
- Python 3.9+
- pnpm 10+ (for frontend)

**Note:** This project uses git submodules for the frontend.

## Quick Start

1. **Clone the repository**

Clone the repository with submodules (the frontend is a shared submodule):

```bash
git clone --recurse-submodules https://github.com/deepgram-starters/flask-text-intelligence.git
cd flask-text-intelligence
```

2. **Install dependencies**

```bash
# Option 1: Use Makefile (recommended)
make init

# Option 2: Manual install
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd frontend && pnpm install && cd ..
```

3. **Set your API key**

Create a `.env` file:

```bash
DEEPGRAM_API_KEY=your_api_key_here
```

4. **Run the app**

**Development mode**:

```bash
make dev
```

**Production mode** (build and serve):

```bash
make build
make start
```

### 🌐 Open the App
[http://localhost:8080](http://localhost:8080)

## Features

- Analyze text with multiple intelligence features:
  - **Summarization** - Generate concise summaries
  - **Topic Detection** - Identify key topics
  - **Sentiment Analysis** - Detect positive/negative sentiment
  - **Intent Recognition** - Understand user intentions
- Input text directly or provide URLs
- View analysis history with localStorage persistence

## Architecture

### Backend
- **Stateless REST API**: Single endpoint `/text-intelligence/analyze`
- Flask server with Deepgram Python SDK
- Supports both text and URL input

### Frontend
- **Pure Vanilla JavaScript** - No frameworks required
- **LocalStorage** - Persistent analysis history
- **Deepgram Design System** - Modern UI styling
- **Shared Submodule** - text-intelligence-html

## How It Works

- **Backend** (`app.py`): Flask server implementing the `/text-intelligence/analyze` endpoint
- **Frontend** (`frontend/`): Vite-powered web UI (shared submodule)
- **API**: Integrates with [Deepgram's Text Intelligence API](https://developers.deepgram.com/docs/text-intelligence)

## API Endpoint

### POST /text-intelligence/analyze

Analyze text with requested intelligence features.

**Request:**
```json
{
  "text": "Your text here"
}
// OR
{
  "url": "https://example.com/text-content"
}
```

**Query Parameters:**
- `summarize` - Generate summary (true/v2)
- `topics` - Detect topics (true)
- `sentiment` - Analyze sentiment (true)
- `intents` - Recognize intents (true)
- `language` - Language code (default: en)

**Response:**
```json
{
  "results": {
    "summary": {...},
    "topics": {...},
    "sentiments": {...},
    "intents": {...}
  }
}
```

## Makefile Commands

```bash
make help              # Show all available commands
make init              # Initialize submodules and install dependencies
make dev               # Start development server
make build             # Build frontend for production
make start             # Start production server
make update            # Update submodules to latest
make clean             # Remove venv, node_modules and build artifacts
make status            # Show git and submodule status
```

## Development

The Flask backend serves the pre-built frontend from `frontend/dist/`. For frontend development, see the [text-intelligence-html repository](https://github.com/deepgram-starters/text-intelligence-html).

## Learn More

- [Deepgram Text Intelligence Documentation](https://developers.deepgram.com/docs/text-intelligence)
- [Deepgram Python SDK](https://github.com/deepgram/deepgram-python-sdk)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

MIT License - see LICENSE file for details.
