# First-AI-Application-using-Qwen-model

## Overview
This repository contains a Flask web application that interacts with the Hugging Face API to generate AI responses using the Qwen model. The app provides a chat interface where users can input prompts and receive AI-generated responses.

## Key Features
- **Chat Interface**: A web-based chat interface for users to interact with the AI model.
- **Session Management**: Maintains a history of user and AI interactions within a session.
- **API Integration**: Connects to the Hugging Face API to generate responses using the Qwen model.
- **Environment Configuration**: Utilizes environment variables for configuration, ensuring sensitive information like API tokens are not hardcoded.

## Key Files
- **README.md**
  - Provides an overview of the project, its features, and setup instructions.
  
- **app.py**
  - Main application file for the Flask web application. Includes:
    - **Initialization**: Loads environment variables and initializes the Flask app.
    - **Routes**:
      - `/`: Renders the chat UI and loads chat history from the session.
      - `/get_response`: Handles chat form submission and retrieves a response from the Hugging Face API.
      - `/clear`: Clears the chat history.
    - **AI Interaction**: Constructs prompts, sends them to the Hugging Face API, and processes the responses.
    - **Session Management**: Maintains chat history within the session and ensures it does not exceed a specified length.

- **.env**
  - Contains environment variables such as `SECRET_KEY` and `HUGGINGFACE_API_TOKEN`. Ensures sensitive information is not hardcoded in the codebase.

## Version and Model Information
- **Flask Version**: The application uses Flask, a lightweight WSGI web application framework.
- **Model**: The application uses the Qwen2.5-Coder-32B-Instruct model from Hugging Face.

## Recommendations
- **Update README.md**: Provide detailed documentation on the project, including setup instructions, usage examples, and any dependencies required.
- **Error Handling**: Ensure robust error handling in `app.py` to manage cases where the API might not respond as expected.
- **Environment Variables**: Safeguard your `.env` file and ensure it contains all necessary environment variables for the application to function correctly.
