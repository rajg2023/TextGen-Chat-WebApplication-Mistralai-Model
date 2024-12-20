document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prompt-form');
    const chatContainer = document.getElementById('chat-container');
    const promptInput = document.getElementById('prompt');

    // Function to simulate typing effect
    function typeMessage(messageElement, message, typingSpeed = 10) {
        let index = 0;
        messageElement.innerHTML = ''; // Clear any previous message content
        let interval = setInterval(() => {
            messageElement.innerHTML += message[index];
            index++;
            if (index === message.length) {
                clearInterval(interval); // Stop typing when the message is complete
            }
        }, typingSpeed);
    }

    // Submit event listener for the form
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userInput = promptInput.value;
        if (!userInput) return;

        // Add user message to chat
        addMessage('user', userInput);
        promptInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `prompt=${encodeURIComponent(userInput)}`
            });
            const data = await response.json();

            // Remove typing indicator
            removeTypingIndicator();

            if (data.error) {
                // Handle API errors gracefully
                addMessage('assistant', data.error);
            } else {
                // Create the AI message element
                const aiMessageElement = document.createElement('div');
                aiMessageElement.classList.add('message', 'assistant');
                chatContainer.appendChild(aiMessageElement);

                // Call the typeMessage function to simulate the typing effect for the AI's response
                typeMessage(aiMessageElement, data.message);
            }

            // Save chat history to session storage
            saveChatHistory();
        } catch (error) {
            console.error('Error fetching AI response:', error);
            addMessage('assistant', 'Error fetching AI response. Please try again later.');
        }
    });

    // Function to add messages to the chat container
    function addMessage(role, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', role);
        messageElement.innerHTML = `<div class="bubble">${message}</div>`;
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Clear chat history event listener
    document.getElementById('clear-chat').addEventListener('click', async () => {
        await fetch('/clear', { method: 'POST' });
        chatContainer.innerHTML = '';
        sessionStorage.removeItem('chatHistory'); // Clear session storage
    });

    // Event listener to send text using Enter key
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    });

    // Load chat history on page load
    window.addEventListener('load', () => {
        // Clear chat container before loading the chat history
        chatContainer.innerHTML = '';
        // Load the chat history from session storage only if it exists and is not empty
        const chatHistory = JSON.parse(sessionStorage.getItem('chatHistory')) || [];
        chatHistory.forEach(message => {
            addMessage(message.role, message.message);
        });
    });

    // Save chat history to session storage
    function saveChatHistory() {
        const messages = Array.from(chatContainer.getElementsByClassName('message')).map(messageElement => {
            const role = messageElement.classList.contains('user') ? 'user' : 'assistant';
            const messageElementBubble = messageElement.querySelector('.bubble');
            const message = messageElementBubble ? messageElementBubble.textContent : '';
            return { role, message };
        });
        sessionStorage.setItem('chatHistory', JSON.stringify(messages));
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');
        typingIndicator.innerHTML = 'Assistant is typing...';
        chatContainer.appendChild(typingIndicator);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            chatContainer.removeChild(typingIndicator);
        }
    }
});
