import os
import secrets
from dotenv import load_dotenv
from flask import Flask, request, render_template, session, jsonify
import requests

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

@app.route('/')
def index():
    """Render the chat UI and load chat history from the session."""
    if 'history' not in session:
        session['history'] = []
    return render_template('chat.html', history=session['history'])

@app.route('/get_response', methods=['POST'])
def get_response():
    """Handle chat form submission and get a response from the HuggingFace API."""
    user_input = request.form.get('prompt', '').strip()
    if not user_input:
        return jsonify({'error': 'Prompt cannot be empty'}), 400

    # Ensure 'history' exists in the session
    if 'history' not in session:
        session['history'] = []

    # Add user message to the session history
    session['history'].append({'role': 'user', 'message': user_input})

    # Prepare the request data for the HuggingFace API
    data = {
        'inputs': f"You: {user_input}\nAI:",  # Sending user input as part of the prompt
        'parameters': {
            'max_length': 100,
            'temperature': 0.7,
            'top_p': 0.95
        }
    }

    try:
        # Send the request to HuggingFace API
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()

        # Extract response text from the API
        response_json = response.json()
        if isinstance(response_json, list) and len(response_json) > 0:
            ai_response = response_json[0].get('generated_text', 'No response')
            # Optionally, split off the prompt part if it's included in the response
            ai_response = ai_response.split('AI:')[-1].strip()  # Extract everything after "AI:"
        else:
            ai_response = 'No valid response received'
    
    except Exception as e:
        ai_response = f"Error: {str(e)}"
    
    # Add AI response to the session history
    session['history'].append({'role': 'assistant', 'message': ai_response})
    session.modified = True  # Ensure session changes are saved
    
    return jsonify({'message': ai_response})

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear the chat history."""
    session.pop('history', None)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)