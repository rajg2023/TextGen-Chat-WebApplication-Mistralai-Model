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
    """Handle chat form submission and get a response from the Hugging Face API."""
    user_input = request.form.get('prompt', '').strip()
    if not user_input:
        return jsonify({'error': 'Prompt cannot be empty'}), 400

    # Ensure 'history' exists in the session
    if 'history' not in session:
        session['history'] = []

    # Limit the history size to the last 5 interactions
    session['history'] = session['history'][-5:]

    # Construct the full prompt without including previous AI responses
    full_prompt = "\n".join(
        f"User: {message['message']}" if message['role'] == 'user' else f"Assistant: {message['message']}"
        for message in session['history'] if message['role'] == 'user'
    )
    full_prompt += f"\nUser: {user_input}\nAssistant:"

    # Calculate input length and ensure minimum tokens for the response
    input_length = len(full_prompt.split())
    context_window_size = 4096
    min_response_tokens = 512
    remaining_tokens = max(context_window_size - input_length, min_response_tokens)

    # Prepare the data to be sent to the Hugging Face API
    data = {
        'inputs': full_prompt,
        'parameters': {
            'max_length': remaining_tokens,
            'temperature': 0.7,
            'top_p': 0.9,
            'stop': ['\nAssistant:']
        }
    }

    try:
        # Send the request to Hugging Face API
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()

        # Extract response text from the API
        response_json = response.json()
        if response_json and isinstance(response_json, list) and len(response_json) > 0:
            ai_response = response_json[0].get('generated_text', 'No response')
        else:
            ai_response = 'No response'

        # Refine response filtering
        if user_input.lower() in ai_response.lower() and len(ai_response.split()) < 20:
            ai_response = "I'm sorry, I couldn't provide a unique response. Please try rephrasing your query."

    except requests.exceptions.RequestException as e:
        # Log error details
        print(f"RequestException: {str(e)}")
        ai_response = f"Error: {str(e)}"

    # Add user message and AI response to the session history
    session['history'].append({'role': 'user', 'message': user_input})
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

print("SECRET_KEY:", os.getenv('SECRET_KEY'))
print("HUGGINGFACE_API_TOKEN:", os.getenv('HUGGINGFACE_API_TOKEN'))