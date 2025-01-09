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
            scrollToBottom(); // Scroll to the bottom after each character is added
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

            // Save chat history to the server
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
        scrollToBottom(); // Scroll to the bottom when a new message is added
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
    window.addEventListener('load', async () => {
        try {
            const response = await fetch('/');
            const data = await response.json();
            const chatHistory = data.history || [];
            chatContainer.innerHTML = ''; // Clear chat container before loading the chat history
            chatHistory.forEach(message => {
                addMessage(message.role, message.message);
            });
            // Save initial history to session storage
            sessionStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    });

    // Save chat history to the server
    async function saveChatHistory() {
        const messages = Array.from(chatContainer.getElementsByClassName('message')).map(messageElement => {
            const role = messageElement.classList.contains('user') ? 'user' : 'assistant';
            const messageElementBubble = messageElement.querySelector('.bubble');
            const message = messageElementBubble ? messageElementBubble.textContent : '';
            return { role, message };
        });

        try {
            await fetch('/save_history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history: messages })
            });
            // Save history to session storage as well
            sessionStorage.setItem('chatHistory', JSON.stringify(messages));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');
        typingIndicator.innerHTML = 'Assistant is typing...';
        chatContainer.appendChild(typingIndicator);
        scrollToBottom(); // Scroll to the bottom when typing indicator is shown
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            chatContainer.removeChild(typingIndicator);
        }
    }

    // Function to scroll to the bottom of the chat container
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
