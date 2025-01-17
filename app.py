import os
import secrets
from dotenv import load_dotenv
from flask import Flask, request, render_template, session, jsonify
import requests
import logging
import json

# Load environment variables from .env
load_dotenv()

# Initialize the Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Get SECRET_KEY from the environment, or fall back to a secure random key
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Load HuggingFace API token from .env
API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
API_URL = 'https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1'

HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("app.log"),
                              logging.StreamHandler()])

HISTORY_FILE = "chat_history.json"

def load_chat_history():
    """Load chat history from a file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    return []

def save_chat_history(history):
    """Save chat history to a file."""
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file)

@app.route('/')
def index():
    if 'initialized' not in session:
        # Start with an initial message and set the initialized flag
        session['history'] = [{'role': 'assistant', 'message': 'Hello! How can I assist you today?'}]
        session['initialized'] = True
        save_chat_history(session['history'])
    else:
        session['history'] = load_chat_history()

    return render_template('chat.html', history=session['history'])

@app.route('/api/inference', methods=['POST'])
def inference():
    data = request.json
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        result = response.json()
        session['ai_response'] = result  # Store the AI response in the session
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return jsonify({"error": "API request failed"}), 500

@app.route('/get_response', methods=['POST'])
def get_response():
    """Process the user input and send it to HuggingFace model."""
    user_input = request.form.get('prompt', '').strip()
    if not user_input:
        logging.warning("Empty prompt received")
        return jsonify({'error': 'Prompt cannot be empty'}), 400

    if 'history' not in session:
        session['history'] = []

    session['history'].append({'role': 'user', 'message': user_input})

    # Limit chat history to avoid context overflow (only last 5 interactions)
    history_for_api = session['history'][-5:]  # Only keep the last 5 exchanges

    # Construct the prompt with the entire conversation history
    messages = [{"role": msg['role'], "content": msg['message']} for msg in history_for_api]
    prompt = apply_chat_template(messages)

    logging.debug(f"Prompt sent to model: {prompt}")

    # Get the AI response
    ai_response = get_complete_ai_response(prompt)

    # Add AI response to the session history
    session['history'].append({'role': 'assistant', 'message': ai_response})
    save_chat_history(session['history'])  # Save the chat history to file
    session.modified = True  # Ensure session changes are saved

    return jsonify({'message': ai_response})

def apply_chat_template(messages):
    """Apply the chat template to format the messages."""
    intro_message = (
        "The following is a conversation with an AI assistant.\n"
        "The assistant is helpful, creative, clever, and concise.\n"
    )
    formatted_messages = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
    return intro_message + formatted_messages + "\nAssistant:"

def get_complete_ai_response(prompt):
    """Send the prompt to HuggingFace API and return the complete response."""
    complete_response = ""
    while True:
        response_part = get_ai_response(prompt + complete_response)
        if response_part.endswith("..."):
            complete_response += response_part[:-3]
        else:
            complete_response += response_part
            break
    return complete_response

def get_ai_response(prompt):
    """Send the prompt to HuggingFace API and return the response."""
    try:
        data = {
            'inputs': prompt,
            'parameters': {
                'max_length': 1000,  # Increase max_length to accommodate longer responses
                'temperature': 0.7,
                'top_p': 0.95
            }
        }

        logging.debug(f"Sending request to HuggingFace API with data: {data}")

        response = requests.post(API_URL, headers=HEADERS, json=data, timeout=60)
        response.raise_for_status()

        response_json = response.json()
        logging.debug(f"Received response from HuggingFace API: {response_json}")

        if isinstance(response_json, list) and len(response_json) > 0:
            generated_text = response_json[0].get('generated_text', 'No response generated.')
            logging.debug(f"Generated text before processing: {generated_text}")
            # Remove the user's message from the AI response if it is included
            if "Assistant:" in generated_text:
                generated_text = generated_text.split("Assistant:")[-1].strip()
            logging.debug(f"Generated text after processing: {generated_text}")
            return generated_text
        else:
            logging.warning("No valid response received from HuggingFace API.")
            return "No valid response received."
    except requests.exceptions.Timeout:
        logging.error("Request to HuggingFace API timed out.")
        return "Error: Request timed out."
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to HuggingFace API failed: {e}")
        return f"Error: {e}"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return f"Error: {e}"

@app.route('/clear', methods=['POST'])
def clear_chat():
    """Clear chat history."""
    session['history'] = []
    save_chat_history([])  # Clear the chat history file
    session.modified = True  # Ensure session changes are saved
    return jsonify({'status': 'success'})

@app.route('/save_history', methods=['POST'])
def save_history():
    """Save the chat history to a file."""
    data = request.json
    history = data.get('history', [])
    save_chat_history(history)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
