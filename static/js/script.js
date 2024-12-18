const form = document.getElementById('chat-form');
const chatContainer = document.getElementById('chat-container');

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
    const promptInput = document.getElementById('prompt');
    const userInput = promptInput.value;
    if (!userInput) return;

    // Add user message to chat
    addMessage('user', userInput);
    promptInput.value = '';

    try {
        const response = await fetch('/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `prompt=${encodeURIComponent(userInput)}`
        });
        const data = await response.json();

        // Create the AI message element
        const aiMessageElement = document.createElement('div');
        aiMessageElement.classList.add('message', 'assistant');
        chatContainer.appendChild(aiMessageElement);

        // Call the typeMessage function to simulate the typing effect for the AI's response
        typeMessage(aiMessageElement, data.message);
    } catch (error) {
        addMessage('assistant', 'Error fetching AI response.');
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
});
