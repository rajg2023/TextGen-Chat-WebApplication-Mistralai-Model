import os
import secrets
from dotenv import load_dotenv
from flask import Flask, request, render_template, session, jsonify, Response
import requests
import logging
import time

# Load environment variables from .env
load_dotenv()

# Initialize the Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Get SECRET_KEY from the environment, or fall back to a secure random key
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Load HuggingFace API token from .env
API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
API_URL = 'https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct'

HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    """Render the chat UI and load chat history from the session."""
    if 'history' not in session:
        session['history'] = []
    return render_template('chat.html', history=session['history'])

@app.route('/get_response', methods=['GET', 'POST'])  # Allow both GET and POST requests
def get_response():
    """Handle both GET and POST requests."""
    if request.method == 'POST':
        user_input = request.form.get('prompt', '').strip()
        if not user_input:
            logging.warning("Empty prompt received")
            return jsonify({'error': 'Prompt cannot be empty'}), 400
    elif request.method == 'GET':
        user_input = request.args.get('prompt', '').strip()  # Fetch prompt from query string
        if not user_input:
            logging.warning("Empty prompt received in GET")
            return jsonify({'error': 'Prompt cannot be empty'}), 400

    if 'history' not in session:
        session['history'] = []

    session['history'].append({'role': 'user', 'message': user_input})

    # ⚠️ Limit chat history to avoid context overflow (only last 10 interactions)
    history_for_api = session['history'][-10:]  # Only keep the last 10 exchanges

    intro_message = (
        "The following is a conversation with an AI assistant.\n"
        "The assistant is helpful, creative, clever, and concise.\n"
    )

    # ⚠️ Enhanced prompt structure for clarity
    prompt = intro_message + "\n".join(
        [f"{msg['role'].capitalize()}: {msg['message']}" for msg in history_for_api]
    ) + "\nAssistant:"

    logging.debug(f"Prompt sent to model: {prompt}")

    # Return a streaming response
    return Response(stream_response(prompt), content_type='text/event-stream')

@app.route('/clear', methods=['POST'])
def clear():
    """Clear the chat history."""
    session.pop('history', None)  # Clear chat history from the session
    return jsonify({'message': 'Chat history cleared'}), 200

def stream_response(prompt, max_loops=10):
    """Stream the AI's response in real-time using SSE."""
    for i in range(max_loops):
        try:
            data = {
                'inputs': prompt, 
                'parameters': {
                    'max_length': 500,  # Generate 500 tokens at a time
                    'temperature': 0.7, 
                    'top_p': 0.95
                }
            }

            logging.info(f"Sending request (loop {i+1})...")
            response = send_request_with_retries(data)
            response_json = response.json()

            if isinstance(response_json, list) and len(response_json) > 0:
                chunk = response_json[0].get('generated_text', '')
                if 'Assistant:' in chunk:
                    chunk = chunk.split('Assistant:')[-1].strip()
                
                logging.debug(f"Received chunk: {chunk}")

                yield f"data: {chunk}\n\n"  # Send the chunk to the client
                
                # ⚠️ Stop the stream when one of the "end" triggers is detected
                if chunk.endswith(('.', '!', '?')) or "The End" in chunk:
                    logging.info("AI finished response.")
                    break

                prompt = prompt + chunk + "\nAssistant:"
            else:
                logging.warning("No valid response received.")
                break

        except Exception as e:
            logging.error(f"Error during generation loop {i+1}: {str(e)}")
            break

def send_request_with_retries(data, retries=3):
    """Send a request to the HuggingFace API with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=HEADERS, json=data, timeout=60)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            if response.status_code == 429:  # Too Many Requests
                time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error occurred: {req_err}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
    raise Exception("All attempts to contact the Qwen API have failed.")

if __name__ == '__main__':
    app.run(debug=True)
