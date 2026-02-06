"""
Flask Text Intelligence Starter - Backend Server

This is a simple Flask server that provides a text intelligence API endpoint
powered by Deepgram's Text Intelligence service. It's designed to be easily
modified and extended for your own projects.

Key Features:
- Contract-compliant API endpoint: POST /text-intelligence/analyze
- Accepts text or URL in JSON body
- Supports multiple intelligence features: summarization, topics, sentiment, intents
- Serves built frontend from frontend/dist/
- CORS enabled for development
"""

import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from deepgram import DeepgramClient
from dotenv import load_dotenv
import toml

# Load .env without overriding existing env vars
load_dotenv(override=False)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Server configuration
CONFIG = {
    "port": int(os.environ.get("PORT", 8081)),
    "host": os.environ.get("HOST", "0.0.0.0"),
    "frontend_port": int(os.environ.get("FRONTEND_PORT", 8080)),
}

# ============================================================================
# API KEY LOADING
# ============================================================================

def load_api_key():
    """
    Loads the Deepgram API key from environment variables
    """
    api_key = os.environ.get("DEEPGRAM_API_KEY")

    if not api_key:
        print("\n❌ ERROR: Deepgram API key not found!\n")
        print("Please set your API key using one of these methods:\n")
        print("1. Create a .env file (recommended):")
        print("   DEEPGRAM_API_KEY=your_api_key_here\n")
        print("2. Environment variable:")
        print("   export DEEPGRAM_API_KEY=your_api_key_here\n")
        print("Get your API key at: https://console.deepgram.com\n")
        raise ValueError("DEEPGRAM_API_KEY environment variable is required")

    return api_key

api_key = load_api_key()

# ============================================================================
# SETUP - Initialize Flask, Deepgram, and middleware
# ============================================================================

# Initialize Deepgram client with API key
deepgram = DeepgramClient(api_key=api_key)

# Initialize Flask app (API server only)
app = Flask(__name__)

# Enable CORS for frontend communication
# Frontend runs on port 8080, backend on port 8081
CORS(app, origins=[
    f"http://localhost:{CONFIG['frontend_port']}",
    f"http://127.0.0.1:{CONFIG['frontend_port']}"
], supports_credentials=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_text_input(body):
    """
    Validates that JSON body has exactly one of text or url

    Args:
        body: Request JSON body

    Returns:
        tuple: (request_dict, error_message)
               request_dict is None if validation fails
    """
    text = body.get('text')
    url = body.get('url')

    # Must have exactly one of text or url
    if not text and not url:
        return None, "Request must contain either 'text' or 'url' field"

    if text and url:
        return None, "Request must contain either 'text' or 'url', not both"

    # Return the request dict for SDK
    if url:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return None, "Invalid URL format"
        return {"url": url}, None
    else:
        # Validate text is not empty
        if not text.strip():
            return None, "Text content cannot be empty"
        return {"text": text}, None

def build_deepgram_options(query_params):
    """
    Converts query parameters to SDK keyword arguments

    Args:
        query_params: Flask request.args object

    Returns:
        dict: Options to pass to Deepgram SDK as **kwargs
    """
    options = {
        'language': query_params.get('language', 'en')
    }

    # Handle summarize parameter (can be 'true', 'v2', or boolean)
    summarize = query_params.get('summarize')
    if summarize == 'true':
        options['summarize'] = True
    elif summarize == 'v2':
        options['summarize'] = 'v2'
    elif summarize == 'v1':
        # v1 is no longer supported
        return None, "Summarization v1 is no longer supported. Please use v2 or true."

    # Boolean features
    if query_params.get('topics') == 'true':
        options['topics'] = True
    if query_params.get('sentiment') == 'true':
        options['sentiment'] = True
    if query_params.get('intents') == 'true':
        options['intents'] = True

    return options, None

def format_error_response(error_type, code, message):
    """
    Formats error responses in a consistent structure per the contract

    Args:
        error_type: "validation_error" or "processing_error"
        code: Error code string
        message: Human-readable error message

    Returns:
        dict: Formatted error response
    """
    return {
        "error": {
            "type": error_type,
            "code": code,
            "message": message,
            "details": {}
        }
    }

# ============================================================================
# API ROUTES
# ============================================================================

@app.route("/text-intelligence/analyze", methods=["POST"])
def analyze():
    """
    POST /text-intelligence/analyze

    Contract-compliant text intelligence endpoint.
    Accepts:
    - Query parameters: summarize, topics, sentiment, intents, language (all optional)
    - Body: JSON with either text or url field (required, not both)

    Returns:
    - Success (200): JSON with results object containing requested intelligence features
    - Error (4XX): JSON error response matching contract format
    """
    try:
        # Validate JSON body
        if not request.is_json:
            error = format_error_response(
                "validation_error",
                "INVALID_TEXT",
                "Request body must be JSON"
            )
            return jsonify(error), 400

        body = request.get_json()

        # Validate text input
        request_dict, error_msg = validate_text_input(body)
        if error_msg:
            error = format_error_response(
                "validation_error",
                "INVALID_TEXT" if "text" in error_msg.lower() else "INVALID_URL",
                error_msg
            )
            return jsonify(error), 400

        # Build Deepgram options from query parameters
        options, error_msg = build_deepgram_options(request.args)
        if error_msg:
            error = format_error_response(
                "validation_error",
                "INVALID_TEXT",
                error_msg
            )
            return jsonify(error), 400

        # Call Deepgram API
        response_data = deepgram.read.v1.text.analyze(
            request=request_dict,
            **options
        )

        # Format response - convert Pydantic model to dict
        if hasattr(response_data, 'to_dict'):
            # SDK v5+ has to_dict() method
            result = {"results": response_data.results.to_dict() if hasattr(response_data.results, 'to_dict') else {}}
        elif hasattr(response_data, 'model_dump'):
            # Pydantic v2 method
            result_data = response_data.model_dump()
            result = {"results": result_data.get('results', {})}
        else:
            # Fallback: try dict() conversion
            result = {"results": dict(response_data.results) if hasattr(response_data, 'results') else {}}

        return jsonify(result), 200

    except Exception as e:
        print(f"Text Intelligence Error: {e}")
        traceback.print_exc()

        # Determine appropriate error code and message
        error_code = "INVALID_TEXT"
        error_message = str(e)
        status_code = 500

        if "text" in str(e).lower():
            error_code = "INVALID_TEXT"
            status_code = 400
        elif "url" in str(e).lower():
            error_code = "INVALID_URL"
            status_code = 400
        elif "too long" in str(e).lower():
            error_code = "TEXT_TOO_LONG"
            status_code = 400

        error = format_error_response(
            "processing_error",
            error_code,
            error_message if status_code == 400 else "Text processing failed"
        )

        return jsonify(error), status_code

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "text-intelligence"}), 200

@app.route("/api/metadata", methods=["GET"])
def get_metadata():
    """
    GET /api/metadata

    Returns metadata about this starter application from deepgram.toml
    Required for standardization compliance
    """
    try:
        with open('deepgram.toml', 'r') as f:
            config = toml.load(f)

        if 'meta' not in config:
            return jsonify({
                'error': 'INTERNAL_SERVER_ERROR',
                'message': 'Missing [meta] section in deepgram.toml'
            }), 500

        return jsonify(config['meta']), 200

    except FileNotFoundError:
        return jsonify({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': 'deepgram.toml file not found'
        }), 500

    except Exception as e:
        print(f"Error reading metadata: {e}")
        return jsonify({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': f'Failed to read metadata from deepgram.toml: {str(e)}'
        }), 500

# ============================================================================
# SERVER START
# ============================================================================

if __name__ == "__main__":
    port = CONFIG["port"]
    host = CONFIG["host"]
    frontend_port = CONFIG["frontend_port"]
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("\n" + "=" * 70)
    print(f"🚀 Flask Text Intelligence Server (Backend API)")
    print("=" * 70)
    print(f"Backend:  http://localhost:{port}")
    print(f"Frontend: http://localhost:{frontend_port}")
    print(f"CORS:     Enabled for frontend port {frontend_port}")
    print(f"Debug:    {'ON' if debug else 'OFF'}")
    print("=" * 70 + "\n")

    app.run(host=host, port=port, debug=debug)
