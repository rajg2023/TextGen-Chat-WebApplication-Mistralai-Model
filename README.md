# Mistralai/Mixtral-8x7B-Instruct-v0.1 ChatAI Web App - (WIP)

This web-based chat application enables users to engage with an AI assistant, leveraging the HuggingFace API for advanced conversational capabilities. The application is meticulously engineered with Flask serving as the backend framework, ensuring robust server-side operations, while the frontend is crafted with HTML and JavaScript, delivering a seamless and interactive user experience.

#**Please note that this is a test application. While it showcases the potential of AI-driven interactions, it may not always provide accurate information and may occasionally generate responses that are not based on factual data, a phenomenon known as "hallucination." Users are advised to proceed with caution and independently verify critical information.

## Features

- **Interactive Chat Interface**: A user-friendly interface that facilitates smooth and engaging conversations between users and the AI assistant.
- **Typing Indicator**: Real-time indicators that display when the AI assistant is generating a response, enhancing the conversational flow.
- **Clear Chat History**: Easily clear the chat history.
- **Session Management**: fficient management of user sessions to maintain context and continuity throughout the interaction.
- **Complete Response Handling**: Ensures long AI responses are complete.

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <ChatAIWebAppname>
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

<p>ChatAIWebApp/<br>├── static/<br>│   ├── css/<br>│   │   └── style.css<br>│   └── js/<br>│       └── script.js<br>├── templates/<br>│   ├── chat.html<br>│   └── error.html<br>├── .env<br>├── app.py<br>├── app.log<br>├── requirements.txt<br>└── README.md</p>


