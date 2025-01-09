# Mistralai/Mixtral-8x7B-Instruct-v0.1 AI Web App - (WIP)

This is a web-based chat application that allows users to interact with an AI assistant powered by the HuggingFace API. Built with Flask for the backend and vanilla JavaScript for the frontend, the app offers an interactive chat interface, typing indicators, session management, and more.

## Features

- **Interactive Chat Interface**: Users can type messages and receive AI-generated responses.
- **Typing Indicator**: Displays when the AI assistant is typing.
- **Clear Chat History**: Easily clear the chat history.
- **Session Management**: Retains chat history across page reloads.
- **Complete Response Handling**: Ensures long AI responses are complete.

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <AIChatAppname>
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file with your HuggingFace API token:
    ```properties
    SECRET_KEY=your_secret_key
    HUGGINGFACE_API_TOKEN=your_huggingface_api_token
    ```

## Usage

1. Run the Flask application:
    ```sh
    flask run
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Start interacting with the AI assistant via the chat interface.

## Project Structure

<p>AIChatApp/<br>├── static/<br>│   ├── css/<br>│   │   └── style.css<br>│   └── js/<br>│       └── script.js<br>├── templates/<br>│   ├── chat.html<br>│   └── error.html<br>├── .env<br>├── app.py<br>├── app.log<br>├── requirements.txt<br>└── README.md</p>


